from django.contrib.postgres.fields import ArrayField
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
    role = models.CharField(max_length=50, default='manager', choices=ROLE_CHOICES)  # roles: manager, hiring_manager, supervisor, human_resources
    is_staff = models.BooleanField(default=False)
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
    other_reason_for_posting = models.CharField(max_length=100, blank=True) # if reason_for_posting is 'others'
    business_unit = models.CharField(max_length=100, choices=BUSINESS_UNIT_CHOICES)
    department_name = models.CharField(max_length=100)
    interview_levels = models.IntegerField()
    immediate_supervisor = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='supervised_prfs')
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'PRF: {self.job_title} - {self.department_name} ({self.business_unit})'