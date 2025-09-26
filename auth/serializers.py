from rest_framework import serializers
from core.models import User
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['is_superuser', 'is_active']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use")
        return value
