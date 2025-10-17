from django.contrib import admin
from .models import CarouselImage, SchoolLogo


@admin.register(CarouselImage)
class CarouselImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    ordering = ['order', '-created_at']


@admin.register(SchoolLogo)
class SchoolLogoAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'uploaded_at']
    list_filter = ['is_active']
