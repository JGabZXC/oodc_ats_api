from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from core.models import User, PRF, Position, Client, ApplicationForm, PipelineStep, JobPosting, AssessmentType, \
    HardwareRequirement, SoftwareRequirement


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

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'department_name', 'working_site', 'status', 'target_start_date', 'reason_for_posting', 'active')
    list_filter = ('status', 'department_name', 'working_site')
    search_fields = ('job_title', 'department_name', 'working_site')
    ordering = ('-target_start_date',)
    list_editable = ('active',)

@admin.register(PRF)
class PRFAdmin(admin.ModelAdmin):
    list_display = ['get_job_title', 'business_unit', 'number_of_vacancies']
    list_filter = ['business_unit', 'job_posting__target_start_date']

    def get_job_title(self, obj):
        return obj.job_posting.job_title if obj.job_posting else '-'
    #
    # get_job_title.short_description = 'Job Title'
    # get_job_title.admin_order_field = 'job_posting__job_title'
    #
    # def get_target_start_date(self, obj):
    #     return obj.job_posting.target_start_date if obj.job_posting else '-'
    #
    # get_target_start_date.short_description = 'Target Start Date'
    # get_target_start_date.admin_order_field = 'job_posting__target_start_date'
    #
    # def get_reason_for_posting(self, obj):
    #     return obj.job_posting.reason_for_posting if obj.job_posting else '-'
    #
    # get_reason_for_posting.short_description = 'Reason for Posting'
    # get_reason_for_posting.admin_order_field = 'job_posting__reason_for_posting'

@admin.register(AssessmentType)
class AssessmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'prfs')
    ordering = ('id',)

@admin.register(HardwareRequirement)
class HardwareRequirementAdmin(admin.ModelAdmin):
    list_display = ('name', 'prfs')
    ordering = ('id',)

@admin.register(SoftwareRequirement)
class SoftwareRequirement(admin.ModelAdmin):
    list_display = ('name', 'prfs')
    ordering = ('id',)

# CLIENT JOB POSTING
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact_number')
    ordering = ('id',)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['get_job_title', 'get_department', 'get_location', 'get_status', 'education_level',
                    'experience_level']
    list_filter = ['education_level', 'experience_level', 'client']

    def get_job_title(self, obj):
        return obj.job_posting.job_title if obj.job_posting else '-'

    get_job_title.short_description = 'Job Title'
    get_job_title.admin_order_field = 'job_posting__job_title'

    def get_department(self, obj):
        return obj.job_posting.department_name if obj.job_posting else '-'

    get_department.short_description = 'Department'
    get_department.admin_order_field = 'job_posting__department_name'

    def get_location(self, obj):
        return obj.job_posting.working_site if obj.job_posting else '-'

    get_location.short_description = 'Location'
    get_location.admin_order_field = 'job_posting__working_site'

    def get_status(self, obj):
        return obj.job_posting.status if obj.job_posting else '-'

    get_status.short_description = 'Status'
    get_status.admin_order_field = 'job_posting__status'

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
                'how_did_you_hear_about_us',
                'agreement',
                'signature'
            ]
        }),
    ]

@admin.register(PipelineStep)
class PipelineStepAdmin(admin.ModelAdmin):
    list_display = ('id', 'position', 'process_type', 'process_title')
    list_filter = ('position',)
    ordering = ('id', 'order',)