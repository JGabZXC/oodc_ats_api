from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from core.models import Position, PRF
from auth.permissions import IsHiringManager
from job.serializers import PositionSerializer
from prf.serializers import PRFSerializer


# Create your views here.
# The edit, delete, get details are only for Position (CLIENT) not PRF
class PositionAV(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsHiringManager()]
        return [AllowAny()]

    def get(self, request):
        my_posts = request.query_params.get('my_posts', 'false').lower() == 'true'
        status = request.query_params.get('status', None)

        if my_posts and request.user.is_authenticated:
            if status == 'no_active':
                prfs = PRF.objects.filter(active=True, posted_by=request.user).exclude(status='active')
                positions = Position.objects.filter(active=True, posted_by=request.user).exclude(status='active')
            else:
                prfs = PRF.objects.filter(active=True, posted_by=request.user, status=status)
                positions = Position.objects.filter(active=True, posted_by=request.user, status=status)
        else:
            prfs = PRF.objects.filter(active=True, published=True)
            positions = Position.objects.filter(active=True, published=True)

        prfs_serializer = PRFSerializer(prfs, many=True)
        positions_serializer = PositionSerializer(positions, many=True)

        prf_data = [
            {**item, "type": "prf"} for item in prfs_serializer.data
        ]
        position_data = [
            {**item, "type": "position"} for item in positions_serializer.data
        ]

        combined = prf_data + position_data
        combined = sorted(combined, key=lambda x: x["created_at"], reverse=True)
        return Response(combined)

    def post(self, request):
        serializer = PositionSerializer(data=request.data)
        if serializer.is_valid():
            position = serializer.save(posted_by=request.user)
            return Response(PositionSerializer(position).data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        ids = request.data.get('ids')

        if not isinstance(ids, list):
            return Response({"error": "Invalid request"}, status=400)

        positions = Position.objects.filter(id__in=ids, active=True)
        if not positions.exists():
            return Response({"error": "No matching Positions found"}, status=status.HTTP_404_NOT_FOUND)

        for position in positions:
            position.active = False
            position.save()

        return Response(status=204)


class PositionDetailAV(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsHiringManager()]
        return [AllowAny()]

    def get_object(self, position_pk):
        try:
            return Position.objects.get(pk=position_pk, active=True)
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
        position.active = False
        position.save()
        return Response(status=204)