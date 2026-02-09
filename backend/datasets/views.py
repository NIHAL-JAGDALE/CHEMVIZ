import pandas as pd
from django.http import HttpResponse
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Dataset, DatasetSummary
from .serializers import (
    DatasetSerializer, 
    DatasetListSerializer, 
    DatasetUploadSerializer,
    DatasetSummarySerializer,
    LoginSerializer,
    RegisterSerializer,
    UserProfileSerializer
)
from .services import parse_csv, generate_summary, enforce_history_limit, generate_pdf_report, CSVValidationError

class UserProfileView(APIView):
    """Handle user profile retrieval and update."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Handle user authentication and token generation."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user is None:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        })


class RegisterView(APIView):
    """Handle user registration and automatic token generation."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'message': 'Account created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Registration failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DatasetUploadView(APIView):
    """Handle CSV file uploads."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = DatasetUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = serializer.validated_data['file']
        
        try:
            # Parse and validate CSV
            df = parse_csv(uploaded_file)
            
            # Reset file pointer for saving
            uploaded_file.seek(0)
            
            # Create dataset
            dataset = Dataset.objects.create(
                user=request.user,
                filename=uploaded_file.name,
                file=uploaded_file
            )
            
            # Generate and save summary
            summary_data = generate_summary(df)
            DatasetSummary.objects.create(
                dataset=dataset,
                total_count=summary_data['total_count'],
                averages=summary_data['averages'],
                type_distribution=summary_data['type_distribution'],
                column_names=summary_data['column_names']
            )
            
            # Enforce history limit
            enforce_history_limit(request.user)
            
            # Return response
            response_data = {
                'dataset_id': str(dataset.id),
                'filename': dataset.filename,
                'timestamp': dataset.uploaded_at.isoformat(),
                'summary': summary_data
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except CSVValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'An error occurred while processing the file: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DatasetListView(APIView):
    """List last 5 uploaded datasets."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        datasets = Dataset.objects.filter(user=request.user).select_related('summary')[:5]
        serializer = DatasetListSerializer(datasets, many=True)
        return Response(serializer.data)


class DatasetSummaryView(APIView):
    """Get full summary for a specific dataset."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, dataset_id):
        try:
            dataset = Dataset.objects.select_related('summary').get(
                id=dataset_id, 
                user=request.user
            )
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = DatasetSerializer(dataset)
        return Response(serializer.data)


class DatasetDataView(APIView):
    """Get raw data from a dataset."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if file exists
        import os
        if not dataset.file or not os.path.exists(dataset.file.path):
            return Response(
                {'error': 'Dataset file not found on server. It may have been deleted.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Try reading with different encodings
            encodings_to_try = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']
            df = None
            last_error = None
            
            for encoding in encodings_to_try:
                try:
                    df = pd.read_csv(dataset.file.path, encoding=encoding, on_bad_lines='warn')
                    break
                except UnicodeDecodeError as e:
                    last_error = e
                    continue
                except Exception as e:
                    last_error = e
                    continue
            
            if df is None:
                return Response(
                    {'error': f'Could not read dataset file: {str(last_error)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            data = df.to_dict(orient='records')
            return Response({
                'columns': df.columns.tolist(),
                'data': data
            })
        except Exception as e:
            return Response(
                {'error': f'Error reading dataset: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReportView(APIView):
    """Generate and return PDF report for a dataset."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, dataset_id):
        try:
            dataset = Dataset.objects.select_related('summary').get(
                id=dataset_id, 
                user=request.user
            )
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            pdf_bytes = generate_pdf_report(dataset)
            
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{dataset.filename.replace(".csv", "")}_report.pdf"'
            return response
            
        except Exception as e:
            return Response(
                {'error': f'Error generating report: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DatasetDetailView(APIView):
    """Retrieve or delete a specific dataset."""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id, user=request.user)
            dataset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

