from django.db import models


class CarouselImage(models.Model):
    """
    Model for carousel images on the frontend
    """
    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='carousel/')
    caption = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0, help_text="Display order (lower numbers appear first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title or f"Carousel Image {self.id}"
    
    class Meta:
        ordering = ['order', '-created_at']


class SchoolLogo(models.Model):
    """
    Model for school logo (only one active logo at a time)
    """
    logo = models.ImageField(upload_to='logo/')
    title = models.CharField(max_length=200, default="School Logo")
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Ensure only one logo is active at a time
        if self.is_active:
            SchoolLogo.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-uploaded_at']
