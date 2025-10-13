from django.urls import path

from client.views import ClientListCreateView, ClientDetailView

urlpatterns = [
    path('', ClientListCreateView.as_view(), name='client-list'),
    path('<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
]