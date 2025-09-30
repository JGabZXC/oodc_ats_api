from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from core.models import User, PRF, Position, Client, ApplicationForm, PipelineStep


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('email', 'first_name', 'last_name', 'role', 'business_unit', 'department', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('email', 'first_name', 'last_name', 'role')
    list_filter = ('role', 'is_active', 'is_staff')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {
            'fields': (
                'first_name',
                'middle_name',
                'last_name',
                'attempt',
                'business_unit',
                'department',
                'role',
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name',
                'middle_name',
                'last_name',
                'business_unit',
                'department',
                'role',
                'is_active',
                'is_staff',
            ),
        }),
    )


@admin.register(PRF)
class PRFAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'target_start_date', 'number_of_vacancies', 'reason_for_posting', 'business_unit')
    search_fields = ('job_title', 'reason_for_posting', 'business_unit')
    list_filter = ('business_unit', 'target_start_date')
    ordering = ('id',)

# CLIENT JOB POSTING
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact_number')
    ordering = ('id',)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'department', 'location', 'status')
    ordering = ('id',)

@admin.register(ApplicationForm)
class ApplicationFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'position')
    ordering = ('id',)
    
    fieldsets = [
        ('Position', {
            'fields': ['position'],
        }),
        ('Personal Information', {
            'fields': [
                'name',
                'birth_date',
                'gender',
                'primary_contact_number',
                'secondary_contact_number',
                'email',
                'linkedin_profile',
                'address',
            ],
        }),
        ('Job Details', {
            'fields': [
                'position_applying_for',
                'expected_salary',
                'willing_to_work_onsite',
                'photo_2x2',
                'upload_med_cert',
                'preferred_interview_schedule'
            ]
        }),
        ('Work and Education', {
            'fields': [
                'education_attained',
                'year_graduated',
                'university',
                'course',
                'work_experience'
            ]
        }),
        ('Acknowledgement', {
            'fields': [
                'how_did_your_hear_about_us',
                'agreement',
                'signature'
            ]
        }),
    ]

@admin.register(PipelineStep)
class PipelineStepAdmin(admin.ModelAdmin):
    list_display = ('id', 'position', 'process_type', 'process_title')
    list_filter = ('position',)
    ordering = ('order',)