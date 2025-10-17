from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PupilProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'full_name', 'role', 'email', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['username', 'full_name', 'email']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('full_name', 'role', 'phone_number', 'profile_image')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('full_name', 'role', 'email', 'phone_number')}),
    )


@admin.register(PupilProfile)
class PupilProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'pupil_class', 'admission_number', 'guardian_name']
    list_filter = ['pupil_class']
    search_fields = ['user__full_name', 'admission_number', 'guardian_name']
