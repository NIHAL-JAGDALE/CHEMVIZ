"""
Tests for the datasets application.
"""
import io
import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status

from .models import Dataset, DatasetSummary
from .services import parse_csv, generate_summary, enforce_history_limit, CSVValidationError


class CSVParsingTests(TestCase):
    """Tests for CSV parsing functionality."""
    
    def test_parse_valid_csv(self):
        """Test parsing a valid CSV file."""
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-001,reactor,15.2,4.5,120
Pump-001,pump,8.5,2.1,45
"""
        file = io.BytesIO(csv_content)
        df = parse_csv(file)
        
        self.assertEqual(len(df), 2)
        self.assertIn('Equipment Name', df.columns)
        self.assertIn('Type', df.columns)
    
    def test_parse_generic_csv(self):
        """Test parsing a generic CSV file with different column names."""
        csv_content = b"""Name,Value,Category
Item-A,100,Alpha
Item-B,200,Beta
"""
        file = io.BytesIO(csv_content)
        df = parse_csv(file)
        
        self.assertEqual(len(df), 2)
        self.assertIn('Name', df.columns)
        self.assertIn('Value', df.columns)
    
    def test_parse_empty_csv(self):
        """Test that parsing fails for empty CSV."""
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure,Temperature
"""
        file = io.BytesIO(csv_content)
        
        with self.assertRaises(CSVValidationError) as context:
            parse_csv(file)
        
        self.assertIn('empty', str(context.exception).lower())


class SummaryGenerationTests(TestCase):
    """Tests for summary generation functionality."""
    
    def test_generate_summary(self):
        """Test summary generation with valid data."""
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-001,reactor,15.0,4.0,120
Reactor-002,reactor,17.0,5.0,130
Pump-001,pump,8.0,2.0,45
Pump-002,pump,10.0,3.0,55
"""
        file = io.BytesIO(csv_content)
        df = parse_csv(file)
        summary = generate_summary(df)
        
        self.assertEqual(summary['total_count'], 4)
        self.assertEqual(summary['averages']['flowrate'], 12.5)
        self.assertEqual(summary['averages']['pressure'], 3.5)
        self.assertEqual(summary['averages']['temperature'], 87.5)
        self.assertEqual(summary['type_distribution']['reactor'], 2)
        self.assertEqual(summary['type_distribution']['pump'], 2)


class HistoryEvictionTests(TestCase):
    """Tests for history limit enforcement."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_enforce_history_limit(self):
        """Test that oldest datasets are deleted when limit is exceeded."""
        # Create 6 datasets
        for i in range(6):
            csv_content = f"""Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-00{i},reactor,15.0,4.0,120
""".encode()
            file = SimpleUploadedFile(f"test_{i}.csv", csv_content)
            dataset = Dataset.objects.create(
                user=self.user,
                filename=f"test_{i}.csv",
                file=file
            )
            DatasetSummary.objects.create(
                dataset=dataset,
                total_count=1,
                averages={'flowrate': 15.0},
                type_distribution={'reactor': 1}
            )
        
        # Apply limit
        enforce_history_limit(self.user, max_datasets=5)
        
        # Should have exactly 5 datasets
        self.assertEqual(Dataset.objects.filter(user=self.user).count(), 5)
        
        # Oldest dataset (test_0.csv) should be deleted
        self.assertFalse(
            Dataset.objects.filter(user=self.user, filename='test_0.csv').exists()
        )


class APITests(TestCase):
    """Tests for API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login(self):
        """Test login endpoint."""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_upload_requires_auth(self):
        """Test that upload endpoint requires authentication."""
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-001,reactor,15.0,4.0,120
"""
        file = SimpleUploadedFile("test.csv", csv_content)
        
        response = self.client.post('/api/upload/', {'file': file})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_upload_csv(self):
        """Test CSV upload with authentication."""
        self.client.force_authenticate(user=self.user)
        
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-001,reactor,15.0,4.0,120
Pump-001,pump,8.0,2.0,45
"""
        file = SimpleUploadedFile("test.csv", csv_content, content_type='text/csv')
        
        response = self.client.post('/api/upload/', {'file': file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('dataset_id', response.data)
        self.assertIn('summary', response.data)
        self.assertEqual(response.data['summary']['total_count'], 2)
    
    def test_list_datasets(self):
        """Test listing datasets."""
        self.client.force_authenticate(user=self.user)
        
        # Upload a dataset
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-001,reactor,15.0,4.0,120
"""
        file = SimpleUploadedFile("test.csv", csv_content, content_type='text/csv')
        self.client.post('/api/upload/', {'file': file}, format='multipart')
        
        response = self.client.get('/api/datasets/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_report(self):
        """Test PDF report generation."""
        self.client.force_authenticate(user=self.user)
        
        # Upload a dataset
        csv_content = b"""Equipment Name,Type,Flowrate,Pressure,Temperature
Reactor-001,reactor,15.0,4.0,120
Pump-001,pump,8.0,2.0,45
"""
        file = SimpleUploadedFile("test.csv", csv_content, content_type='text/csv')
        upload_response = self.client.post('/api/upload/', {'file': file}, format='multipart')
        dataset_id = upload_response.data['dataset_id']
        
        response = self.client.get(f'/api/report/{dataset_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
