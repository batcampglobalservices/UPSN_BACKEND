from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Class, Subject
from .serializers import ClassSerializer, ClassListSerializer, SubjectSerializer
from accounts.permissions import IsAdmin, IsAdminOrTeacher


from backend.realtime import broadcast_update

class ClassViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        instance = serializer.save()
        broadcast_update('class_update', {'action': 'create', 'class_id': instance.id})
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        broadcast_update('class_update', {'action': 'update', 'class_id': instance.id})
        return instance

    def perform_destroy(self, instance):
        class_id = instance.id
        instance.delete()
        broadcast_update('class_update', {'action': 'delete', 'class_id': class_id})
    """
    ViewSet for Class CRUD operations
    Admin: Full access
    Teacher: View only their assigned classes
    Pupil: View their own class
    """
    permission_classes = [IsAuthenticated]
    filterset_fields = ['level', 'assigned_teacher']
    search_fields = ['name', 'level']
    ordering_fields = ['name', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ClassListSerializer
        return ClassSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Optimize with select_related and prefetch_related"""
        user = self.request.user
        base_queryset = Class.objects.select_related('assigned_teacher').prefetch_related('pupils')
        
        if user.role == 'admin':
            return base_queryset.all()
        elif user.role == 'teacher':
            return base_queryset.filter(assigned_teacher=user)
        elif user.role == 'pupil':
            # Pupils see only their own class
            try:
                pupil_profile = user.pupil_profile
                if pupil_profile.pupil_class:
                    return base_queryset.filter(id=pupil_profile.pupil_class.id)
            except:
                pass
        return Class.objects.none()
    
    @method_decorator(cache_page(180))  # Cache for 3 minutes
    def list(self, request, *args, **kwargs):
        """Cached list of classes"""
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def pupils(self, request, pk=None):
        """Get all pupils in a class"""
        class_obj = self.get_object()
        from accounts.serializers import PupilProfileSerializer
        # Optimize pupil query with select_related
        pupils = class_obj.pupils.select_related('user').all()
        serializer = PupilProfileSerializer(pupils, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save()
        broadcast_update('class_update', {'action': 'create', 'class_id': instance.id})
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        broadcast_update('class_update', {'action': 'update', 'class_id': instance.id})
        return instance

    def perform_destroy(self, instance):
        class_id = instance.id
        instance.delete()
        broadcast_update('class_update', {'action': 'delete', 'class_id': class_id})


class SubjectViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, 'role', None) == 'teacher':
            assigned_class = serializer.validated_data.get('assigned_class')
            if not assigned_class or assigned_class.assigned_teacher_id != user.id:
                raise PermissionDenied('Teachers can only create subjects for classes assigned to them.')

            provided_teacher = serializer.validated_data.get('assigned_teacher')
            if provided_teacher and provided_teacher.id != user.id:
                raise PermissionDenied('Teachers can only assign themselves as the subject teacher.')

            instance = serializer.save(assigned_teacher=user)
            from backend.realtime import broadcast_update
            broadcast_update('subject_update', {'action': 'create', 'subject_id': instance.id})
            return instance

        instance = serializer.save()
        from backend.realtime import broadcast_update
        broadcast_update('subject_update', {'action': 'create', 'subject_id': instance.id})
        return instance

    def perform_update(self, serializer):
        user = self.request.user
        if getattr(user, 'role', None) == 'teacher':
            instance = self.get_object()
            new_class = serializer.validated_data.get('assigned_class', instance.assigned_class)
            if not new_class or new_class.assigned_teacher_id != user.id:
                raise PermissionDenied('Teachers can only modify subjects for classes assigned to them.')

            provided_teacher = serializer.validated_data.get('assigned_teacher', user)
            if provided_teacher and provided_teacher.id != user.id:
                raise PermissionDenied('Teachers can only assign themselves as the subject teacher.')

            instance = serializer.save(assigned_teacher=user, assigned_class=new_class)
            from backend.realtime import broadcast_update
            broadcast_update('subject_update', {'action': 'update', 'subject_id': instance.id})
            return instance

        instance = serializer.save()
        from backend.realtime import broadcast_update
        broadcast_update('subject_update', {'action': 'update', 'subject_id': instance.id})
        return instance

    def perform_destroy(self, instance):
        subject_id = instance.id
        instance.delete()
        from backend.realtime import broadcast_update
        broadcast_update('subject_update', {'action': 'delete', 'subject_id': subject_id})
    """
    ViewSet for Subject CRUD operations
    Admin: Full access
    Teacher: Can create, view, and update subjects they teach or in their assigned classes
    """
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['assigned_class', 'assigned_teacher']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    
    def get_permissions(self):
        # Allow both admins and teachers to create/update subjects
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAdminOrTeacher()]
        elif self.action == 'destroy':
            # Only admins can delete subjects
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Optimize with select_related to prevent N+1 queries"""
        from django.db import models
        user = self.request.user
        base_queryset = Subject.objects.select_related('assigned_class', 'assigned_teacher')
        
        if user.role == 'admin':
            return base_queryset.all()
        elif user.role == 'teacher':
            # Teachers can see subjects in their assigned classes or subjects they teach
            return base_queryset.filter(
                models.Q(assigned_teacher=user) | 
                models.Q(assigned_class__assigned_teacher=user)
            ).distinct()
        elif user.role == 'pupil':
            # Pupils see subjects in their class
            try:
                pupil_profile = user.pupil_profile
                if pupil_profile.pupil_class:
                    return base_queryset.filter(assigned_class=pupil_profile.pupil_class)
            except:
                pass
        return Subject.objects.none()
    
    def list(self, request, *args, **kwargs):
        """
        List subjects without caching to ensure real-time visibility
        for score entry and subject management
        """
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Teachers can only create subjects for their own classes and must assign themselves."""
        user = self.request.user
        if getattr(user, 'role', None) == 'teacher':
            assigned_class = serializer.validated_data.get('assigned_class')
            if not assigned_class or assigned_class.assigned_teacher_id != user.id:
                raise PermissionDenied('Teachers can only create subjects for classes assigned to them.')

            # If assigned_teacher provided and is not the current user, block
            provided_teacher = serializer.validated_data.get('assigned_teacher')
            if provided_teacher and provided_teacher.id != user.id:
                raise PermissionDenied('Teachers can only assign themselves as the subject teacher.')

            serializer.save(assigned_teacher=user)
            return

        # Admins can set any fields
        serializer.save()

    def perform_update(self, serializer):
        """Teachers can only update subjects in their classes and cannot assign other teachers."""
        user = self.request.user
        if getattr(user, 'role', None) == 'teacher':
            instance = self.get_object()

            # Check class ownership: either existing or new assigned_class if provided
            new_class = serializer.validated_data.get('assigned_class', instance.assigned_class)
            if not new_class or new_class.assigned_teacher_id != user.id:
                raise PermissionDenied('Teachers can only modify subjects for classes assigned to them.')

            # Enforce teacher assignment to self
            provided_teacher = serializer.validated_data.get('assigned_teacher', user)
            if provided_teacher and provided_teacher.id != user.id:
                raise PermissionDenied('Teachers can only assign themselves as the subject teacher.')

            serializer.save(assigned_teacher=user, assigned_class=new_class)
            return

        # Admins
        serializer.save()


from django.db import models

