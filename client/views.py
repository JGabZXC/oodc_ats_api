from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth.permissions import IsHiringManager
from client.serializers import ClientSerializer
from core.models import Client

# Create your views here.
class ClientListCreateView(ListCreateAPIView):
    queryset = Client.objects.filter(active=True)
    serializer_class = ClientSerializer
    pagination_class = None # To do: Add pagination later

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsHiringManager()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

class ClientDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    lookup_field = 'pk'

    # To do: When updating a client make sure to record an update history showing who made the change.
    # To do: When deleting a client only soft delete instead of permanently removing it

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsHiringManager()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)