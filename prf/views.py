from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth.permissions import IsHiringManager
from core.models import PRF
from prf.serializers import PRFSerializer


# Create your views here.

class PrfAV(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsHiringManager()]
        return [AllowAny()]

    def get(self, request):
        prfs = PRF.objects.all()
        serializer = PRFSerializer(prfs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PRFSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(posted_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)