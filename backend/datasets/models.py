import uuid
from django.db import models
from django.contrib.auth.models import User


class Dataset(models.Model):
    """Model to store uploaded CSV datasets."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"


class DatasetSummary(models.Model):
    """Model to store computed summary statistics for a dataset."""
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE, related_name='summary')
    total_count = models.IntegerField()
    averages = models.JSONField(default=dict)  # {"flowrate": 12.3, "pressure": 3.4, ...}
    type_distribution = models.JSONField(default=dict)  # {"reactor": 40, "pump": 30, ...}
    column_names = models.JSONField(default=list)  # List of column names in the CSV
    
    def __str__(self):
        return f"Summary for {self.dataset.filename}"
