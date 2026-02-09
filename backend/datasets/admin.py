from django.contrib import admin
from .models import Dataset, DatasetSummary


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['filename', 'user', 'uploaded_at']
    list_filter = ['uploaded_at', 'user']
    search_fields = ['filename']
    readonly_fields = ['id', 'uploaded_at']


@admin.register(DatasetSummary)
class DatasetSummaryAdmin(admin.ModelAdmin):
    list_display = ['dataset', 'total_count']
    search_fields = ['dataset__filename']
