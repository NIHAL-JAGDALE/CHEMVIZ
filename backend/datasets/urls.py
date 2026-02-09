from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    DatasetUploadView,
    DatasetListView,
    DatasetDetailView,
    DatasetSummaryView,
    DatasetDataView,
    ReportView,
    UserProfileView
)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('upload/', DatasetUploadView.as_view(), name='upload'),
    path('datasets/', DatasetListView.as_view(), name='dataset-list'),
    path('datasets/<uuid:dataset_id>/', DatasetDetailView.as_view(), name='dataset-detail'),
    path('summary/<uuid:dataset_id>/', DatasetSummaryView.as_view(), name='dataset-summary'),
    path('data/<uuid:dataset_id>/', DatasetDataView.as_view(), name='dataset-data'),
    path('report/<uuid:dataset_id>/', ReportView.as_view(), name='dataset-report'),
]
