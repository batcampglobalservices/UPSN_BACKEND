from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class AcademicSession(models.Model):
    """
    Model for academic sessions (e.g., 2024/2025)
    """
    TERM_CHOICES = (
        ('first', 'First Term'),
        ('second', 'Second Term'),
        ('third', 'Third Term'),
    )
    
    name = models.CharField(max_length=20, unique=True, help_text="e.g., 2024/2025")
    start_date = models.DateField()
    end_date = models.DateField()
    current_term = models.CharField(
        max_length=10,
        choices=TERM_CHOICES,
        default='first',
        help_text="Current active term for this session"
    )
    is_active = models.BooleanField(default=True)
    result_release_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Date and time when results will be released to pupils"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-start_date']


class Result(models.Model):
    """
    Model for pupil results
    """
    TERM_CHOICES = (
        ('first', 'First Term'),
        ('second', 'Second Term'),
        ('third', 'Third Term'),
    )
    
    GRADE_CHOICES = (
        ('A', 'A (Excellent)'),
        ('B', 'B (Very Good)'),
        ('C', 'C (Good)'),
        ('D', 'D (Pass)'),
        ('F', 'F (Fail)'),
    )
    
    pupil = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='results',
        limit_choices_to={'role': 'pupil'}
    )
    subject = models.ForeignKey(
        'classes.Subject',
        on_delete=models.CASCADE,
        related_name='results'
    )
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='results'
    )
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    test_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        help_text="Test score out of 30"
    )
    exam_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(70)],
        help_text="Exam score out of 70"
    )
    total = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, editable=False)
    teacher_comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calculate total
        self.total = self.test_score + self.exam_score
        
        # Calculate grade
        if self.total >= 70:
            self.grade = 'A'
        elif self.total >= 60:
            self.grade = 'B'
        elif self.total >= 50:
            self.grade = 'C'
        elif self.total >= 45:
            self.grade = 'D'
        else:
            self.grade = 'F'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.pupil.full_name} - {self.subject.name} - {self.term} {self.session}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['pupil', 'subject', 'session', 'term']
        indexes = [
            models.Index(fields=['pupil', 'session', 'term'], name='result_pupil_sess_term_idx'),
            models.Index(fields=['session', 'term'], name='result_sess_term_idx'),
            models.Index(fields=['subject'], name='result_subject_idx'),
            models.Index(fields=['-created_at'], name='result_created_idx'),
        ]


class ResultSummary(models.Model):
    """
    Model for overall result summary per term/session
    """
    pupil = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='result_summaries'
    )
    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name='summaries'
    )
    term = models.CharField(max_length=10, choices=Result.TERM_CHOICES)
    total_subjects = models.IntegerField(default=0)
    total_score = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overall_grade = models.CharField(max_length=1, choices=Result.GRADE_CHOICES)
    principal_comment = models.TextField(blank=True, null=True)
    teacher_comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_summary(self):
        """Calculate and update summary from results"""
        results = Result.objects.filter(
            pupil=self.pupil,
            session=self.session,
            term=self.term
        )
        
        self.total_subjects = results.count()
        if self.total_subjects > 0:
            self.total_score = sum([result.total for result in results])
            self.average_score = self.total_score / self.total_subjects
            
            # Calculate overall grade
            if self.average_score >= 70:
                self.overall_grade = 'A'
            elif self.average_score >= 60:
                self.overall_grade = 'B'
            elif self.average_score >= 50:
                self.overall_grade = 'C'
            elif self.average_score >= 45:
                self.overall_grade = 'D'
            else:
                self.overall_grade = 'F'
        else:
            self.total_score = 0
            self.average_score = 0
            self.overall_grade = 'F'
        
        self.save()
    
    def __str__(self):
        return f"{self.pupil.full_name} - {self.term} {self.session}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['pupil', 'session', 'term']
        verbose_name_plural = 'Result Summaries'
        indexes = [
            models.Index(fields=['pupil', 'session', 'term'], name='summary_pupil_sess_term_idx'),
            models.Index(fields=['session', 'term'], name='summary_sess_term_idx'),
            models.Index(fields=['-created_at'], name='summary_created_idx'),
        ]

