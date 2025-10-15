from django.urls import path
#
from job.views import JobPostingView, JobPostingViewDelete

urlpatterns = [
    path('', JobPostingView.as_view(), name='position-list'),
    path('bulk-delete/', JobPostingViewDelete.as_view(), name='position-bulk-delete'),
]