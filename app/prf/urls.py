from django.urls import path
from . import views
urlpatterns = [
    path('', views.PrfAV.as_view(), name='prf-list-create')
]