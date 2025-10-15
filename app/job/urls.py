from django.urls import path
#
from job.views import JobPostingView, JobPostingViewDelete, JobPostingDetailView

urlpatterns = [
    path('', JobPostingView.as_view(), name='position-list'),
    path('<int:pk>/', JobPostingDetailView.as_view(), name='position-details'),
    path('bulk-delete/', JobPostingViewDelete.as_view(), name='position-bulk-delete'),
]