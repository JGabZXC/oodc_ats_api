from django.db import transaction

from client.serializers import ClientSerializer
from core.models import Position, ApplicationForm, PipelineStep, JobPosting, Client
from rest_framework import serializers

from job.serializers import JobPostingSerializer

class ApplicationFormSerializer(serializers.ModelSerializer):
    position = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ApplicationForm
        fields = '__all__'

class PipelineStepSerializer(serializers.ModelSerializer):
    position = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.IntegerField(required=False)
    _delete = serializers.BooleanField(required=False, write_only=True)
    process_type_display = serializers.SerializerMethodField()

    class Meta:
        model = PipelineStep
        fields = '__all__'

    def get_process_type_display(self, obj):
        return obj.get_process_type_display()

class PositionSerializer(serializers.ModelSerializer):
    job_posting = JobPostingSerializer(write_only=True)
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    application_form = ApplicationFormSerializer(required=True)
    pipeline = PipelineStepSerializer(many=True, required=True)

    class Meta:
        model = Position
        fields = '__all__'

    def validate_pipeline(self, value):
        if not value:
            raise serializers.ValidationError("At least one pipeline step is required.")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['client'] = str(instance.client)

        return representation

    @transaction.atomic
    def create(self, validated_data):
        client_data = validated_data.pop('client')
        job_posting_data = validated_data.pop('job_posting')
        application_form_data = validated_data.pop('application_form')
        pipeline_steps_data = validated_data.pop('pipeline', [])

        job_posting_data['posted_by'] = self.context['request'].user
        job_posting_data['type'] = 'client'
        job_posting_data['published'] = True # Since it's a client it is directly published, no need of approval
        job_posting_data['status'] = 'active'
        job_posting = JobPosting.objects.create(**job_posting_data)

        position = Position.objects.create(client=client_data, job_posting=job_posting, **validated_data)

        application_form_data['position'] = position
        ApplicationForm.objects.create(**application_form_data)

        for step_data in pipeline_steps_data:
            step_data['position'] = position
            PipelineStep.objects.create(**step_data)

        return position



