from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('token/refresh/', views.refresh_token, name='refresh_token'),
    path('test/', views.test_protected_view, name='protected_route'),
]