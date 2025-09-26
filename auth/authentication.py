from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from rest_framework_simplejwt.exceptions import InvalidToken

from core.models import User


class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        if request.path == '/api/user/login/':
            return None

        header = self.get_header(request)

        if header is None:
            raw_token = request.COOKIES.get(
                settings.SIMPLE_JWT.get('AUTH_COOKIE')
            )
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        try:
            current_user = User.objects.get(id=user.id)
            if not current_user.is_active or current_user.attempt >= 5:
                raise InvalidToken('User account is inactive or locked')

            # Check if current role matches token role
            token_role = validated_token.get('role')
            token_department = validated_token.get('department')
            token_business_unit = validated_token.get('business_unit')

            print(f"Token Role: {token_role}, User Role: {current_user.role}")
            print(f"Token Department: {token_department}, User Department: {current_user.department}")
            print(f"Token Business Unit: {token_business_unit}, User Business Unit: {current_user.business_unit}")
            if current_user.role != token_role:
                raise InvalidToken('User role has changed, please login again')

            if current_user.department != token_department:
                raise InvalidToken('User department has changed, please login again')

            if current_user.business_unit != token_business_unit:
                raise InvalidToken('User business unit has changed, please login again')

            return current_user, validated_token
        except User.DoesNotExist:
            raise InvalidToken('User not found')