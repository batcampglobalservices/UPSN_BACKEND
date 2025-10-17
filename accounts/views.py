from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import CustomUser, PupilProfile
from .serializers import (
    UserSerializer, PupilProfileSerializer, LoginSerializer, 
    UserCreateSerializer, UserProfileSerializer
)
from .permissions import IsAdmin, IsAdminOrTeacher


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations
    Only accessible by Admin
    """
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'full_name', 'email']
    ordering_fields = ['created_at', 'full_name']
    
    def get_queryset(self):
        """Optimize with select_related for pupil profiles"""
        return CustomUser.objects.select_related('pupil_profile').all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'message': 'User deactivated successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'message': 'User activated successfully'}, status=status.HTTP_200_OK)


class PupilProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PupilProfile
    Teachers can view and edit pupils in their class
    Pupils can only view their own profile
    """
    serializer_class = PupilProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        # Optimize with select_related to prevent N+1 queries
        base_queryset = PupilProfile.objects.select_related(
            'user', 
            'pupil_class',
            'pupil_class__assigned_teacher'
        )
        
        if user.role == 'admin':
            return base_queryset.all()
        elif user.role == 'teacher':
            # Teachers can only see pupils in their assigned classes
            from classes.models import Class
            teacher_classes = Class.objects.filter(assigned_teacher=user)
            return base_queryset.filter(pupil_class__in=teacher_classes)
        elif user.role == 'pupil':
            # Pupils can only see their own profile
            return base_queryset.filter(user=user)
        return PupilProfile.objects.none()


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login endpoint that returns JWT tokens
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'Account is deactivated'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'role': user.role,
            'email': user.email,
            'phone_number': user.phone_number,
            'profile_image': user.profile_image.url if user.profile_image else None,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdmin])
def register_view(request):
    """
    Register endpoint for creating new users (Admin only)
    """
    serializer = UserCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    
    return Response({
        'message': 'User created successfully',
        'user': UserSerializer(user).data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get current user profile
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update current user profile
    """
    serializer = UserSerializer(
        request.user, 
        data=request.data, 
        partial=True,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response({
        'message': 'Profile updated successfully',
        'user': UserProfileSerializer(request.user).data
    }, status=status.HTTP_200_OK)

