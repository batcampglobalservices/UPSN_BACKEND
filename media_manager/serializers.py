from rest_framework import serializers
from .models import CarouselImage, SchoolLogo


class CarouselImageSerializer(serializers.ModelSerializer):
    """
    Serializer for CarouselImage model
    """
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CarouselImage
        fields = ['id', 'title', 'image', 'image_url', 'caption', 'order', 
                  'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        return None


class SchoolLogoSerializer(serializers.ModelSerializer):
    """
    Serializer for SchoolLogo model
    """
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SchoolLogo
        fields = ['id', 'logo', 'logo_url', 'title', 'is_active', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
    
    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        elif obj.logo:
            return obj.logo.url
        return None
