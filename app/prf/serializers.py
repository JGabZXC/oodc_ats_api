from django.db import transaction
from rest_framework import serializers

from core.models import PRF, AssessmentType, HardwareRequirement, SoftwareRequirement, JobPosting
from job.serializers import JobPostingSerializer

# Helper Function
def _update_related_items(instance, data, model_class, relation_name):
    if data is None:
        return

    for item in data:
        if isinstance(item, dict):
            item_id = item.get('id')
            name = item.get('name')
            if item_id:
                try:
                    obj = model_class.objects.get(id=item_id, prfs=instance)
                    obj.name = name
                    obj.save()
                except model_class.DoesNotExist:
                    pass
            else:
                # Either create new item if no id provided but for now pass
                pass

class AssessmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentType
        fields = ['id', 'name']

class HardwareRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = HardwareRequirement
        fields = ['id', 'name']

class SoftwareRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftwareRequirement
        fields = ['id', 'name']

class PRFSerializer(serializers.ModelSerializer):
    job_posting = JobPostingSerializer()

    # Write-only fields for creation
    assessment_types = serializers.ListField(write_only=True, required=False)
    hardware_requirements = serializers.ListField(write_only=True, required=False)
    software_requirements = serializers.ListField(write_only=True, required=False)

    # Read-only fields for output
    assessment_types_list = AssessmentTypeSerializer(source='assessment_types', many=True, read_only=True)
    hardware_requirements_list = HardwareRequirementSerializer(source='hardware_requirements', many=True, read_only=True)
    software_requirements_list = SoftwareRequirementSerializer(source='software_requirements', many=True, read_only=True)
    class Meta:
        model = PRF
        fields = '__all__'
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Replace the write-only fields with the read-only nested serializer output
        data['assessment_types'] = data.pop('assessment_types_list')
        data['hardware_requirements'] = data.pop('hardware_requirements_list')
        data['software_requirements'] = data.pop('software_requirements_list')
        return data

    @transaction.atomic
    def create(self, validated_data):
        job_posting_data = validated_data.pop('job_posting')
        assessment_types_data = validated_data.pop('assessment_types', [])
        hardware_requirements_data = validated_data.pop('hardware_requirements', [])
        software_requirements_data = validated_data.pop('software_requirements', [])
        hiring_managers_data = validated_data.pop('hiring_managers', [])

        job_posting_data['posted_by'] = self.context['request'].user
        job_posting_data['type'] = 'prf'
        job_posting = JobPosting.objects.create(**job_posting_data)
        prf = PRF.objects.create(job_posting=job_posting, **validated_data)
        prf.hiring_managers.set(hiring_managers_data)

        for assessment_name in assessment_types_data:
            AssessmentType.objects.create(prfs=prf, name=assessment_name)
        for hardware_name in hardware_requirements_data:
            HardwareRequirement.objects.create(prfs=prf, name=hardware_name)
        for software_name in software_requirements_data:
            SoftwareRequirement.objects.create(prfs=prf, name=software_name)

        return prf

    @transaction.atomic
    def update(self, instance, validated_data):
        job_posting_data = validated_data.pop('job_posting', {})
        assessment_types_data = validated_data.pop('assessment_types', None)
        hardware_requirements_data = validated_data.pop('hardware_requirements', None)
        software_requirements_data = validated_data.pop('software_requirements', None)
        hiring_managers_data = validated_data.pop('hiring_managers', None)

        if job_posting_data:
            new_status = job_posting_data.get('status')
            if new_status and new_status != instance.job_posting.status:
                # Fix the logic later if approval logic is implemented
                approved_by_managers = validated_data.get('approved_by_managers', 0)
                try:
                    instance.job_posting.set_status(new_status, approved_by_managers)
                except ValueError as e:
                    raise serializers.ValidationError({'detail': str(e)})
                job_posting_data.pop('status')
            for attr, value in job_posting_data.items():
                setattr(instance.job_posting, attr, value)
            instance.job_posting.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if hiring_managers_data is not None:
            instance.hiring_managers.set(hiring_managers_data)

        _update_related_items(instance, assessment_types_data, AssessmentType, 'assessment_types')
        _update_related_items(instance, hardware_requirements_data, HardwareRequirement, 'hardware_requirements')
        _update_related_items(instance, software_requirements_data, SoftwareRequirement, 'software_requirements')

        return instance
