from django.db import transaction
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth.permissions import IsHiringManager
from core.models import PRF
from prf.serializers import PRFSerializer


# Create your views here.

class PrfAV(APIView):
    def get_permissions(self):
        if self.request.method == 'POST' and self.request.method == 'DELETE':
            return [IsHiringManager()]
        return [IsAuthenticated()]

    def get(self, request):
        prfs = PRF.objects.filter(job_posting__active=True)
        serializer = PRFSerializer(prfs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PRFSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        ids = request.data.pop('ids', None)

        if isinstance(ids, list):
            prfs = PRF.objects.filter(id__in=ids)
            deleted_count, _ = prfs.delete()
            return Response (status=status.HTTP_204_NO_CONTENT)

        return Response({'error': 'Invalid data. "ids" should be a list of PRF IDs.'}, status=status.HTTP_400_BAD_REQUEST)

class PrfDetails(RetrieveUpdateDestroyAPIView):
    queryset = PRF.objects.filter(job_posting__active=True)
    serializer_class = PRFSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsHiringManager()]
        return [IsAuthenticated()]