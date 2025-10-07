from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinLengthValidator, MaxLengthValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin, Permission, Group
)
from django.db.models import JSONField


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('hiring_manager', 'Hiring Manager'),
        ('supervisor', 'Supervisor'),
        ('human_resources', 'Human Resources'),
    ]
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255)
    attempt = models.IntegerField(default=0)
    business_unit = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=50, default='manager',
                            choices=ROLE_CHOICES)  # roles: manager, hiring_manager, supervisor, human_resources
    is_staff = models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.')
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def __str__(self):
        return self.email


class PRF(models.Model):
    BUSINESS_UNIT_CHOICES = [
        ('oodc', 'OODC'),
        ('oors', 'OORS'),
    ]

    job_title = models.CharField(max_length=255)
    target_start_date = models.DateField()
    number_of_vacancies = models.IntegerField()
    reason_for_posting = models.CharField(max_length=100)
    other_reason_for_posting = models.CharField(max_length=100, blank=True)  # if reason_for_posting is 'others'
    business_unit = models.CharField(max_length=100, choices=BUSINESS_UNIT_CHOICES)
    department_name = models.CharField(max_length=100)
    interview_levels = models.IntegerField()
    immediate_supervisor = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE,
                                             related_name='supervised_prfs')
    hiring_managers = models.ManyToManyField(
        User,
        related_name='prfs_as_hiring_manager',
        blank=True
    )
    contract_type = models.CharField(max_length=100)
    work_arrangement = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    working_site = models.CharField(max_length=100)
    work_schedule_from = models.TimeField()
    work_schedule_to = models.TimeField()
    job_description = models.TextField()
    responsibilities = models.TextField()
    qualifications = models.TextField()
    non_negotiables = models.TextField(blank=True)
    salary_budget = models.DecimalField(max_digits=10, decimal_places=2)
    is_salary_range = models.BooleanField(default=False)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2)
    assessment_required = models.BooleanField(default=False)
    assessment_types = JSONField(default=dict, null=True, blank=True)
    other_assessment = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    hardware_required = JSONField(default=dict, null=True, blank=True)
    software_required = JSONField(default=dict, null=True, blank=True)
    published = models.BooleanField(default=False)

    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='posted_prfs', null=True)  # Change this later, posted_by should not be null or blank
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'PRF: {self.job_title} - {self.department_name} ({self.business_unit})'


# FOR CLIENT JOB POSTING SYSTEM
class Client(models.Model):
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255)
    contact_number = models.CharField(validators=[
        MinLengthValidator(11),
        MaxLengthValidator(11)
    ])

    active = models.BooleanField(default=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='clients', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('doctorate', 'Doctorate Degree'),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('executive', 'Executive'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]

    WORK_SETUP_CHOICES = [
        ('onsite', 'Onsite'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='positions', null=True)
    job_title = models.CharField(max_length=255)
    education_level = models.CharField(max_length=255, choices=EDUCATION_LEVEL_CHOICES)
    department = models.CharField(max_length=255)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVEL_CHOICES)
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE_CHOICES)
    headcount = models.IntegerField(validators=[MaxValueValidator(100)], default=0)
    work_setup = models.CharField(max_length=50, choices=WORK_SETUP_CHOICES)
    date_needed = models.DateField()

    reason_for_hiring = models.CharField(max_length=255)
    other_reason_for_hiring = models.CharField(max_length=255, blank=True,
                                               null=True)  # if reason_for_hiring is 'others'
    min_budget = models.DecimalField(max_digits=10, decimal_places=2)
    max_budget = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    responsibilities = models.TextField()
    qualifications = models.TextField()
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')

    published = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='posted_positions', null=True)  # Change this later, posted_by should not be null or blank
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.job_title} - {self.client.name}'


# Step 3
# This model will define the application form such as if the field is required, optional, or disabled
class ApplicationForm(models.Model):
    FIELDS_CHOICES = [
        ('required', 'Required'),
        ('optional', 'Optional'),
        ('disabled', 'Disabled'),
    ]

    position = models.OneToOneField(Position, on_delete=models.CASCADE, related_name='application_form')
    name = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    birth_date = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    gender = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    primary_contact_number = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    secondary_contact_number = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    email = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    linkedin_profile = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    address = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')

    # This should be disabled always since the position applying for is already known
    # position_applying_for = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    expected_salary = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    willing_to_work_onsite = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    photo_2x2 = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    upload_med_cert = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    preferred_interview_schedule = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')

    education_attained = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    year_graduated = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    university = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    course = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    work_experience = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')

    how_did_you_hear_about_us = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    agreement = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')
    signature = models.CharField(max_length=50, choices=FIELDS_CHOICES, default='optional')

    def __str__(self):
        return f'{self.position.job_title} - {self.position.client.name}'


class PipelineStep(models.Model):
    PROCESS_TYPE_CHOICES = [
        ('resume_screening', 'Resume Screening'),
        ('phone_interview', 'Phone Interview'),
        ('initial_interview', 'Initial Interview'),
        ('assessments', 'Assessments'),
        ('final_interview', 'Final Interview'),
        ('offer', 'Offer'),
        ('onboarding', 'Onboarding'),
    ]

    STAGE_CHOICES = [
        (1, 'Stage 1'),
        (2, 'Stage 2'),
        (3, 'Stage 3'),
        (4, 'Stage 4'),
    ]

    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='pipeline')
    process_type = models.CharField(max_length=50, choices=PROCESS_TYPE_CHOICES)
    process_title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(
        help_text='Order of this step within its stage (1, 2, 3, etc.)'
    )
    stage = models.PositiveIntegerField(
        choices=STAGE_CHOICES,
        help_text='Which stage this step belongs to (1-4)'
    )

    class Meta:
        unique_together = ('position', 'stage', 'order',)
        ordering = ['stage', 'order']

    def __str__(self):
        return f'{self.position.job_title} - {self.process_title}'
