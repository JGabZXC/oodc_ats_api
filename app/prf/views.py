from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
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
        prfs = PRF.objects.filter(active=True)
        serializer = PRFSerializer(prfs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PRFSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(posted_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        ids = request.data.get('ids')

        if not isinstance(ids, list):
            return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        prfs = PRF.objects.filter(id__in=ids, active=True)
        if not prfs.exists():
            return Response({"error": "No matching PRFs found"}, status=status.HTTP_404_NOT_FOUND)

        for prf in prfs:
            prf.active = False
            prf.save()

        return Response( status=status.HTTP_200_OK)

class PrfDetails(RetrieveUpdateDestroyAPIView):
    queryset = PRF.objects.all()
    serializer_class = PRFSerializer
    lookup_field = 'pk'
    permission_classes = [IsHiringManager]

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
