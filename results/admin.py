from django.contrib import admin
from .models import Result, AcademicSession, ResultSummary


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['pupil', 'subject', 'session', 'term', 'test_score', 'exam_score', 'total', 'grade']
    list_filter = ['session', 'term', 'grade']
    search_fields = ['pupil__full_name', 'subject__name']


@admin.register(ResultSummary)
class ResultSummaryAdmin(admin.ModelAdmin):
    list_display = ['pupil', 'session', 'term', 'total_subjects', 'average_score', 'overall_grade']
    list_filter = ['session', 'term', 'overall_grade']
    search_fields = ['pupil__full_name']
