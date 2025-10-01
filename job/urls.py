from django.urls import path

from job.views import PositionAV, PositionDetailAV

urlpatterns = [
    path('', PositionAV.as_view(), name='position-list-create'),
    path('<int:position_pk>/', PositionDetailAV.as_view(), name='position-detail'),
]