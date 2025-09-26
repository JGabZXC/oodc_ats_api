from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from core.models import User, PRF


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
