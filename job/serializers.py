from rest_framework import serializers
from django.db import transaction
from core.models import Client, Position, ApplicationForm, PipelineStep


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ApplicationFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationForm
        fields = '__all__'
        extra_kwargs = {
            'position': {'required': False}
        }


class PipelineStepSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    _delete = serializers.BooleanField(required=False, write_only=True)
    process_type_display = serializers.SerializerMethodField()

    class Meta:
        model = PipelineStep
        exclude = ['position']

    def get_process_type_display(self, obj):
        return obj.get_process_type_display()


class PositionSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    application_form = ApplicationFormSerializer(required=True)
    pipeline = PipelineStepSerializer(many=True, required=True)
    work_setup_display = serializers.SerializerMethodField()
    experience_level_display = serializers.SerializerMethodField()
    employment_type_display = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = '__all__'

    def get_work_setup_display(self, obj):
        return obj.get_work_setup_display()

    def get_experience_level_display(self, obj):
        return obj.get_experience_level_display()

    def get_employment_type_display(self, obj):
        return obj.get_employment_type_display()

    def create(self, validated_data):
        application_form_data = validated_data.pop('application_form')
        pipeline_data = validated_data.pop('pipeline')
        print(validated_data)

        with transaction.atomic():
            position = Position.objects.create(**validated_data)
            ApplicationForm.objects.create(position=position, **application_form_data)
            for step_data in pipeline_data:
                PipelineStep.objects.create(position=position, **step_data)

        return position

    def update(self, instance, validated_data):
        app_form_data = validated_data.pop('application_form', None)
        pipeline_data = validated_data.pop('pipeline', None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if app_form_data is not None:
                ApplicationForm.objects.update_or_create(
                    position=instance, defaults=app_form_data
                )

            if pipeline_data is not None:
                for step_data in pipeline_data:
                    step_id = step_data.get('id')

                    if step_data.get('_delete') and step_id:
                        PipelineStep.objects.filter(id=step_id).delete()

                    if step_id:
                        try:
                            step = PipelineStep.objects.get(position=instance, id=step_id)
                            for key, value in step_data.items():
                                setattr(step, key, value)
                            step.save()
                        except PipelineStep.DoesNotExist:
                            raise serializers.ValidationError({'error': "Pipeline step does not exist"})
                    else:
                        required_fields = ['process_type', 'process_title', 'description', 'order', 'stage']
                        missing = [f for f in required_fields if f not in step_data]
                        if missing:
                            raise serializers.ValidationError(
                                {'error': f"Missing required fields for new PipelineStep: {missing}"}
                            )
                        PipelineStep.objects.create(position=instance, **step_data)

            return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['client'] = str(
            instance.client)  # This is to show the client name instead of id in read operations only
        return representation
