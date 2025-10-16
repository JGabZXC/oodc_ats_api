from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth.permissions import IsHiringManager
from core.models import Position
from position.serializers import PositionSerializer


# Create your views here.
class PositionListView(ListCreateAPIView):
    queryset = Position.objects.filter(job_posting__active=True)
    serializer_class = PositionSerializer

    def get_permissions(self):
        if self.request.method == 'POST' and self.request.method == 'DELETE':
            return [IsHiringManager()]
        return [IsAuthenticated()]

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        return super().get_serializer(*args, **kwargs)



    # def get(self, request):
    #     positions = Position.objects.filter(job_posting__active=True)
    #     serializer = PositionSerializer(positions, many=True)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    #
    # def post(self, request):
    #     serializer = PositionSerializer(data=request.data, context={'request': request})
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
