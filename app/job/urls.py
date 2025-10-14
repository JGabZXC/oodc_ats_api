from django.urls import path
#
from job.views import JobPostingView

urlpatterns = [
    path('', JobPostingView.as_view(), name='position-list'),
]