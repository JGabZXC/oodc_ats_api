from rest_framework import serializers
from core.models import JobPosting

class JobPostingSerializer(serializers.ModelSerializer):
    type_display = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = '__all__'
        read_only_fields = ['type', 'published'] # Inorder to set it as 'prf' in PRFSerializer
        # Validation comes first before creating, we are already setting it in PRFSerializer create method

    def get_type_display(self, obj):
        return obj.get_type_display()

    def destroy(self, instance):
        self.instance.active = False
        self.instance.save()

        return instance