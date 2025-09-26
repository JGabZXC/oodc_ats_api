from rest_framework import serializers
from core.models import User
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        exclude = ['is_superuser', 'is_active', 'is_staff', 'user_permissions', 'groups', 'last_login', 'attempt']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)  # This properly hashes the password
        user.save()
        return user

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use")
        return value
