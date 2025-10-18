from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CarouselImage, SchoolLogo
from .serializers import CarouselImageSerializer, SchoolLogoSerializer
from accounts.permissions import IsAdmin


class CarouselImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CarouselImage CRUD operations
    Public can view active images
    Only Admin can create/edit/delete
    """
    queryset = CarouselImage.objects.all()
    serializer_class = CarouselImageSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'active_images']:
            return [AllowAny()]
        return [IsAdmin()]
    
    def get_queryset(self):
        if self.action == 'active_images' or (self.action in ['list', 'retrieve'] and not self.request.user.is_authenticated):
            return CarouselImage.objects.filter(is_active=True)
        return CarouselImage.objects.all()
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def active_images(self, request):
        """Get all active carousel images"""
        images = CarouselImage.objects.filter(is_active=True)
        serializer = self.get_serializer(images, many=True)
        return Response(serializer.data)


class SchoolLogoViewSet(viewsets.ModelViewSet):
    from rest_framework.parsers import MultiPartParser, FormParser
    parser_classes = [MultiPartParser, FormParser]
    """
    ViewSet for SchoolLogo operations
    Public can view active logo
    Only Admin can upload/update
    """
    queryset = SchoolLogo.objects.all()
    serializer_class = SchoolLogoSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'active_logo']:
            return [AllowAny()]
        return [IsAdmin()]
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def active_logo(self, request):
        """Get the active school logo"""
        logo = SchoolLogo.objects.filter(is_active=True).first()
        if logo:
            serializer = self.get_serializer(logo)
            return Response(serializer.data)
        return Response({'error': 'No active logo found'}, status=status.HTTP_404_NOT_FOUND)

