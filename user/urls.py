from django.urls import path
from .views import UserViewAV

urlpatterns = [
    path('', UserViewAV.as_view(), name='user-list-create'),
    path('<str:filter_bu>', UserViewAV.as_view(), name='user-list-create'),

]
