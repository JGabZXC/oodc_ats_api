from rest_framework import serializers
from core.models import PRF, User


class PRFSerializer(serializers.ModelSerializer):
    unique_id = serializers.SerializerMethodField(read_only=True)
    hiring_managers = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
    )
    immediate_supervisor_display = serializers.SerializerMethodField()
    employment_type_display = serializers.SerializerMethodField()
    work_setup_display = serializers.SerializerMethodField()
    type_display = serializers.SerializerMethodField()

    class Meta:
        model = PRF
        fields = '__all__'

    def get_immediate_supervisor(self, obj):
        if obj.immediate_supervisor:
            return f"{obj.immediate_supervisor.first_name} {obj.immediate_supervisor.last_name}"
        return None

    def get_immediate_supervisor_display(self, obj):
        if obj.immediate_supervisor:
            return f"{obj.immediate_supervisor.first_name} {obj.immediate_supervisor.last_name}"
        return None

    def get_unique_id(self, obj):
        return f"prf_{obj.id}"
    def get_employment_type_display(self, obj):
        return obj.get_employment_type_display()
    def get_work_setup_display(self, obj):
        return obj.get_work_setup_display()
    def get_type_display(self, obj):
        return obj.get_type_display()

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