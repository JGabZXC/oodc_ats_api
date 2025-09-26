from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth.authentication import CookieJWTAuthentication
from auth.permissions import IsSuperAdmin
from user.serializers import UserSerializer
from core.models import User


# Create your views here.
class UserViewAV(APIView):
    authentication_classes = [CookieJWTAuthentication]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated()]

    def post(self, request):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, filter_bu=None):
        if filter_bu:
            users = User.objects.filter(business_unit=filter_bu, is_active=True)
        else:
            users = User.objects.filter(is_active=True)

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

