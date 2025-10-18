from django.db import models
from django.conf import settings


class Class(models.Model):
    """
    Model for school classes (JSS1-SS3)
    """
    CLASS_CHOICES = (
        ('JK1', 'JK1'),
        ('JK2', 'JK2'),
        ('JK3', 'JK3'),
        ('SK', 'SK'),
        ('GRADE 1', 'GRADE 1'),
        ('GRADE 2', 'GRADE 2'),
        ('GRADE 3', 'GRADE 3'),
        ('GRADE 4', 'GRADE 4'),
        ('GRADE 5', 'GRADE 5'),
    )
    
    name = models.CharField(max_length=50, unique=True, help_text="e.g., JK1A, GRADE 2B")
    level = models.CharField(max_length=10, choices=CLASS_CHOICES)
    assigned_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_classes',
        limit_choices_to={'role': 'teacher'}
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['level', 'name']
        verbose_name_plural = 'Classes'
        indexes = [
            models.Index(fields=['level'], name='class_level_idx'),
            models.Index(fields=['assigned_teacher'], name='class_teacher_idx'),
            models.Index(fields=['-created_at'], name='class_created_idx'),
        ]


class Subject(models.Model):
    """
    Model for subjects taught in classes
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    assigned_class = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    assigned_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_subjects',
        limit_choices_to={'role': 'teacher'}
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.assigned_class.name}"
    
    class Meta:
        ordering = ['assigned_class', 'name']
        unique_together = ['name', 'assigned_class']
        indexes = [
            models.Index(fields=['assigned_class'], name='subject_class_idx'),
            models.Index(fields=['assigned_teacher'], name='subject_teacher_idx'),
            models.Index(fields=['-created_at'], name='subject_created_idx'),
        ]
