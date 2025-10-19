from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import DatabaseError
import logging

from .models import CarouselImage, SchoolLogo, SiteSetting
from .serializers import CarouselImageSerializer, SchoolLogoSerializer, SiteSettingSerializer
from accounts.permissions import IsAdmin

logger = logging.getLogger(__name__)


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

class SiteSettingViewSet(viewsets.ModelViewSet):
    """Simple API for site settings. Admin-only for create/update/delete."""
    queryset = SiteSetting.objects.all()
    serializer_class = SiteSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Allow anonymous read access so the public frontend can fetch theme settings
        if self.action in ['list', 'retrieve', 'get_by_key']:
            return [AllowAny()]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def get_by_key(self, request):
        key = request.query_params.get('key')
        if not key:
            return Response({'error': 'key query param required'}, status=400)
        try:
            setting = SiteSetting.objects.filter(key=key).first()
        except DatabaseError as exc:
            # Common in deployments where migrations haven't been run yet (missing table)
            logger.exception("Database error when fetching SiteSetting for key=%s", key)
            return Response({'error': 'database_error', 'detail': 'SiteSetting table may not exist yet'}, status=503)

        if not setting:
            return Response({'key': key, 'value': {}}, status=200)
        serializer = self.get_serializer(setting)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except DatabaseError:
            logger.exception("Database error while creating SiteSetting")
            return Response({'error': 'database_error', 'detail': 'Could not save site setting (database error).'}, status=503)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except DatabaseError:
            logger.exception("Database error while updating SiteSetting")
            return Response({'error': 'database_error', 'detail': 'Could not update site setting (database error).'}, status=503)

    def partial_update(self, request, *args, **kwargs):
        try:
            return super().partial_update(request, *args, **kwargs)
        except DatabaseError:
            logger.exception("Database error while partially updating SiteSetting")
            return Response({'error': 'database_error', 'detail': 'Could not update site setting (database error).'}, status=503)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except DatabaseError:
            logger.exception("Database error while deleting SiteSetting")
            return Response({'error': 'database_error', 'detail': 'Could not delete site setting (database error).'}, status=503)

