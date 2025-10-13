from rest_framework import serializers
from core.models import Client

class ClientSerializer(serializers.ModelSerializer):
    posted_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Client
        fields = '__all__'

    def get_posted_by(self, obj):
        return f"{obj.posted_by.first_name} {obj.posted_by.last_name}" if obj.posted_by else None