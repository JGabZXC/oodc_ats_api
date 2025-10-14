from rest_framework import serializers
from core.models import JobPosting

class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = '__all__'
        read_only_fields = ['type'] # Inorder to set it as 'prf' in PRFSerializer
        # Validation comes first before creating, we are already setting it in PRFSerializer create method