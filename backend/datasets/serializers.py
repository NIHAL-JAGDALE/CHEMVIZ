from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset, DatasetSummary


class DatasetSummarySerializer(serializers.ModelSerializer):
    """Serializer for dataset summary."""
    
    class Meta:
        model = DatasetSummary
        fields = ['total_count', 'averages', 'type_distribution', 'column_names']


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for dataset with embedded summary."""
    summary = DatasetSummarySerializer(read_only=True)
    
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at', 'summary']


class DatasetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for dataset list."""
    total_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at', 'total_count']
    
    def get_total_count(self, obj):
        if hasattr(obj, 'summary'):
            return obj.summary.total_count
        return None


class DatasetUploadSerializer(serializers.Serializer):
    """Serializer for CSV upload."""
    file = serializers.FileField()
    
    def validate_file(self, value):
        # Check file extension
        if not value.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")
        
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        return value


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration."""
    username = serializers.CharField(max_length=150, min_length=3)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True)
    
    def validate_username(self, value):
        """Check if username already exists."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value
    
    def validate_email(self, value):
        """Check if email already exists."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value
    
    def validate(self, data):
        """Check that passwords match."""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data
    
    def create(self, validated_data):
        """Create and return a new user."""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile update."""
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True, required=False, min_length=6)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password']
        read_only_fields = ['id']

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def validate(self, data):
        if 'password' in data:
            if 'confirm_password' not in data:
                raise serializers.ValidationError({"confirm_password": "Confirm password is required."})
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
