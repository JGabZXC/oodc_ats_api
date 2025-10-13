from django.urls import path
from . import views
urlpatterns = [
    path('', views.PrfAV.as_view(), name='prf-list-create'),
    path('<int:pk>/', views.PrfDetails.as_view(), name='prf-details-update-delete')
]