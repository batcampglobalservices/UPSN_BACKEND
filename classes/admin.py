from django.contrib import admin
from .models import Class, Subject


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'assigned_teacher', 'created_at']
    list_filter = ['level']
    search_fields = ['name', 'assigned_teacher__full_name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'assigned_class', 'assigned_teacher', 'created_at']
    list_filter = ['assigned_class']
    search_fields = ['name', 'code', 'assigned_teacher__full_name']
