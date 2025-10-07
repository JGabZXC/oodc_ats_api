from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from core.models import Position
from auth.permissions import IsHiringManager
from job.serializers import PositionSerializer


# Create your views here.
class PositionAV(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsHiringManager()]
        return [AllowAny()]

    def get(self, request):
        positions = Position.objects.filter(active=True, published=True)
        serializer = PositionSerializer(positions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PositionSerializer(data=request.data)
        if serializer.is_valid():
            position = serializer.save(posted_by=request.user)
            return Response(PositionSerializer(position).data, status=201)
        return Response(serializer.errors, status=400)

class PositionDetailAV(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsHiringManager()]
        return [AllowAny()]

    def get_object(self, position_pk):
        try:
            return Position.objects.get(pk=position_pk)
        except Position.DoesNotExist:
            return None

    def get(self, request, position_pk):
        position = self.get_object(position_pk)
        if not position:
            return Response({"error": "Position not found"}, status=404)
        serializer = PositionSerializer(position)
        return Response(serializer.data)

    def patch(self, request, position_pk):
        position = self.get_object(position_pk)
        if not position:
            return Response({"error": "Position not found"}, status=404)
        serializer = PositionSerializer(position, data=request.data, partial=True)
        if serializer.is_valid():
            position = serializer.save()
            return Response(PositionSerializer(position).data)
        return Response(serializer.errors, status=400)

    def delete(self, request, position_pk):
        position = self.get_object(position_pk)
        if not position:
            return Response({"error": "Position not found"}, status=404)
        position.delete()
        return Response(status=204)