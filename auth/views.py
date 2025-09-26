from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from app import settings
from auth.authentication import CookieJWTAuthentication
from user.serializers import UserSerializer
from core.models import User

REFRESH_TOKEN_LIFETIME= settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME')
ACCESS_TOKEN_LIFETIME= settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME')

def check_account_locked(user):
    if user.attempt >= 5:
        return Response({
            'detail': 'Account Locked. Please ask administrator!'
        }, status=status.HTTP_403_FORBIDDEN)
    return None

def send_token(user):
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    access_token['role'] = user.role
    access_token['department'] = user.department
    access_token['business_unit'] = user.business_unit

    customRes = Response({
        'detail': 'Login successful',
        'user': UserSerializer(user, many=False).data,
        'access': str(access_token)
    }, status=status.HTTP_200_OK)

    customRes.set_cookie(
        'access_token',
        str(access_token),
        max_age=int(ACCESS_TOKEN_LIFETIME.total_seconds()),
        httponly=True,
        secure=True,
        samesite='None'
    )
    customRes.set_cookie(
        'refresh_token',
        str(refresh),
        max_age=int(REFRESH_TOKEN_LIFETIME.total_seconds()),
        httponly=True,
        secure=True,
        samesite='None'
    )

    return customRes

# Create your views here.
@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, email=request.data['email'])

    if check_account_locked(user):
        return check_account_locked(user)

    if not user.is_active:
        return Response({
            'detail': 'User account is inactive.'
        }, status=status.HTTP_403_FORBIDDEN)

    if not user.check_password(request.data['password']):
        user.attempt += 1
        user.save()

        if check_account_locked(user):
            return check_account_locked(user)

        return Response({
            'detail': f'Wrong password. Please try again. {5 - user.attempt} remaining attempt/s.'
        }, status=status.HTTP_400_BAD_REQUEST)

    if user.attempt > 0:
        user.attempt = 0
        user.save()

    return send_token(user)

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    access_token = request.COOKIES.get('access_token')
    ref_token = request.COOKIES.get('refresh_token')

    if not access_token and not ref_token:
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    response = Response({"message": "Logout successful"}, status=status.HTTP_204_NO_CONTENT)
    response.set_cookie('access_token', '', max_age=0,
                        httponly=True, secure=False, samesite="Strict")
    response.set_cookie('refresh_token', '', max_age=0,
                        httponly=True, secure=False, samesite="Strict")

    return response

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    ref_tok = request.COOKIES.get('refresh_token')
    if not ref_tok:
        return Response({
            'detail': 'Authentication credentials were not provided.'
        }, status=status.HTTP_401_UNAUTHORIZED)

    try:
        refresh = RefreshToken(ref_tok)
        user_id = refresh.payload.get('user_id')

        try:
            user = get_object_or_404(User, id=user_id)
        except User.DoesNotExist:
            return Response({
                'detail': 'User not found'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'detail': 'User account is inactive'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if user.attempt >= 5:
            return Response({
                'detail': 'Account is locked'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return send_token(user)
    except Exception as e:
        return Response({
            'detail': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieJWTAuthentication])
def test_protected_view(request):
    if request.user.role != "hiring_manager":
        return Response({"message": "You do not have permission to access this view"}, status=status.HTTP_403_FORBIDDEN)
    return Response({"message": "This is a protected view"}, status=status.HTTP_200_OK)