from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    """
    Custom User model with role-based access
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('pupil', 'Pupil'),
    )
    
    # Override username to accept only numeric values
    username = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(regex='^[0-9]+$', message='Username must be numeric')],
        help_text='Numeric username only'
    )
    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='pupil')
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} - {self.full_name} ({self.role})"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role'], name='user_role_idx'),
            models.Index(fields=['is_active'], name='user_active_idx'),
            models.Index(fields=['-created_at'], name='user_created_idx'),
        ]


class PupilProfile(models.Model):
    """
    Extended profile for pupils with additional academic information
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='pupil_profile')
    pupil_class = models.ForeignKey('classes.Class', on_delete=models.SET_NULL, null=True, blank=True, related_name='pupils')
    admission_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    guardian_name = models.CharField(max_length=200, blank=True, null=True)
    guardian_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.full_name} - {self.pupil_class}"
    
    class Meta:
        ordering = ['user__full_name']
        indexes = [
            models.Index(fields=['pupil_class'], name='pupil_class_idx'),
            models.Index(fields=['user'], name='pupil_user_idx'),
        ]
