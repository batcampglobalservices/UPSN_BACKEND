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
    
    def create(self, request, *args, **kwargs):
        """Custom create to handle user creation with proper response"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Creating user with data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        logger.info(f"User created successfully: {user.username} (ID: {user.id})")
        
        # Return the user with UserSerializer to include all fields
        output_serializer = UserSerializer(user)
        headers = self.get_success_headers(output_serializer.data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
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
    
    def destroy(self, request, *args, **kwargs):
        """Custom delete with logging and cascade handling"""
        import logging
        logger = logging.getLogger(__name__)
        
        user = self.get_object()
        username = user.username
        user_id = user.id
        user_role = user.role
        
        logger.warning(f"🗑️ Deleting user: {username} (ID: {user_id}, Role: {user_role})")
        
        try:
            # Django will handle cascading deletes based on model relationships
            self.perform_destroy(user)
            logger.info(f"✅ User {username} deleted successfully")
            
            return Response({
                'message': f'User {username} deleted successfully',
                'deleted_user_id': user_id,
                'deleted_username': username
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"❌ Error deleting user {username}: {str(e)}")
            return Response({
                'error': 'Failed to delete user',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


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

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def set_class(self, request, pk=None):
        """Allow admin to set or clear the pupil's class"""
        profile = self.get_object()
        pupil_class_id = request.data.get('pupil_class')

        # Allow clearing the class by sending empty string or null
        if pupil_class_id in ['', None]:
            profile.pupil_class = None
            profile.save()
            return Response({'message': 'Pupil class cleared successfully'}, status=status.HTTP_200_OK)

        try:
            # Accept numeric id
            profile.pupil_class_id = int(pupil_class_id)
            profile.save()
            return Response({'message': 'Pupil class updated successfully'}, status=status.HTTP_200_OK)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid pupil_class id'}, status=status.HTTP_400_BAD_REQUEST)


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


@api_view(['POST'])
@permission_classes([IsAdmin])
def set_pupil_class_view(request):
    """Admin endpoint to set or clear a pupil's class by pupil_profile id or user id.

    Accepts JSON payload: { "profile_id": <id>, "pupil_class": <class_id> }
    If `pupil_class` is null or empty, the class will be cleared.
    """
    profile_id = request.data.get('profile_id')
    user_id = request.data.get('user_id')
    pupil_class_id = request.data.get('pupil_class')

    if not profile_id and not user_id:
        return Response({'error': 'profile_id or user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if profile_id:
            profile = PupilProfile.objects.get(id=profile_id)
        else:
            profile = PupilProfile.objects.get(user_id=user_id)
    except PupilProfile.DoesNotExist:
        return Response({'error': 'PupilProfile not found'}, status=status.HTTP_404_NOT_FOUND)

    if pupil_class_id in ['', None]:
        profile.pupil_class = None
        profile.save()
        return Response({'message': 'Pupil class cleared successfully'}, status=status.HTTP_200_OK)

    try:
        profile.pupil_class_id = int(pupil_class_id)
        profile.save()
        return Response({'message': 'Pupil class updated successfully'}, status=status.HTTP_200_OK)
    except (TypeError, ValueError):
        return Response({'error': 'Invalid pupil_class id'}, status=status.HTTP_400_BAD_REQUEST)

