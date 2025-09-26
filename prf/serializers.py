from rest_framework import serializers
from core.models import PRF, User


class PRFSerializer(serializers.ModelSerializer):
    hiring_managers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
    )

    immediate_supervisor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = PRF
        fields = '__all__'

    def to_internal_value(self, data):
        if data.get('immediate_supervisor') == 'no_supervisor':
            data = data.copy()
            data['immediate_supervisor'] = None
        return super().to_internal_value(data)

    def validate_immediate_supervisor(self, value):
        if value == "no_supervisor":
            return None
        return value

    def validate_hiring_managers(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('hiring_managers must be a list.')

        return value

    def validate(self, data):
        # Handle interview_levels based on hiring_managers
        if not data.get('hiring_managers'):  # Empty list or None
            data['interview_levels'] = 0

        return data