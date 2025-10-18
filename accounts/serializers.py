from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, PupilProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model
    """
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    pupil_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'full_name', 'role', 'email', 
                  'phone_number', 'profile_image', 'is_active', 'pupil_profile', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'pupil_profile']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False, 'allow_blank': True},
            'email': {'required': False, 'allow_blank': True, 'allow_null': True}
        }
    
    def validate_password(self, value):
        """Only validate password if it's provided and not blank"""
        if value and value.strip():
            validate_password(value)
            return value
        return value
    
    def validate_email(self, value):
        """Convert empty string to None for email uniqueness"""
        if not value or not value.strip():
            return None
        return value
    
    def validate_phone_number(self, value):
        """Convert empty string to None for phone_number"""
        if not value or not value.strip():
            return None
        return value
    
    def validate_username(self, value):
        """Validate username is numeric and unique (excluding current instance)"""
        if not value or not value.strip():
            raise serializers.ValidationError("Username is required")
        
        # Check if username already exists (excluding current instance during update)
        instance = self.instance
        if instance:
            # This is an update - check if username changed and if new username exists
            if instance.username != value:
                if CustomUser.objects.filter(username=value).exclude(id=instance.id).exists():
                    raise serializers.ValidationError("A user with this username already exists")
        else:
            # This is a create - just check if username exists
            if CustomUser.objects.filter(username=value).exists():
                raise serializers.ValidationError("A user with this username already exists")
        
        return value
    
    def get_pupil_profile(self, obj):
        """Return pupil profile data if user is a pupil"""
        if obj.role == 'pupil':
            try:
                profile = obj.pupil_profile
                return {
                    'id': profile.id,
                    'pupil_class': profile.pupil_class.id if profile.pupil_class else None,
                    'pupil_class_name': profile.pupil_class.name if profile.pupil_class else None,
                    'admission_number': profile.admission_number,
                }
            except PupilProfile.DoesNotExist:
                return None
        return None
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        
        # Handle empty email
        if 'email' in validated_data and not validated_data['email']:
            validated_data['email'] = None
            
        user = CustomUser.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        
        # Auto-create PupilProfile if role is pupil
        if user.role == 'pupil':
            PupilProfile.objects.create(user=user)
        
        return user
    
    def update(self, instance, validated_data):
        # Only admin can update username and password
        request = self.context.get('request')
        if request and request.user.role != 'admin':
            validated_data.pop('username', None)
            validated_data.pop('password', None)
        
        # Remove password from validated_data (will handle separately)
        password = validated_data.pop('password', None)
        
        # Handle empty email - convert to None
        if 'email' in validated_data and not validated_data['email']:
            validated_data['email'] = None
        
        # Handle empty phone_number - convert to None
        if 'phone_number' in validated_data and not validated_data['phone_number']:
            validated_data['phone_number'] = None
        
        # Extract pupil_class if provided (admins may set this)
        pupil_class = None
        # If request included pupil_class in payload (not part of validated_data because it's on profile),
        # it may be available on self.context['request'].data
        request = self.context.get('request')
        if request and getattr(request.user, 'role', None) == 'admin':
            try:
                # Support DRF Request (.data) or Django HttpRequest (.POST/.body)
                request_data = None
                if hasattr(request, 'data'):
                    request_data = request.data
                elif hasattr(request, 'POST'):
                    request_data = request.POST
                else:
                    # Try parsing JSON body
                    try:
                        import json
                        if hasattr(request, 'body') and request.body:
                            request_data = json.loads(request.body.decode('utf-8'))
                    except Exception:
                        request_data = None

                # Accept either 'pupil_class' at root or inside 'pupil_profile'
                if isinstance(request_data, dict):
                    if 'pupil_class' in request_data:
                        pupil_class = request_data.get('pupil_class')
                    elif 'pupil_profile' in request_data and isinstance(request_data['pupil_profile'], dict):
                        pupil_class = request_data['pupil_profile'].get('pupil_class')
            except Exception:
                pupil_class = None

        # Update all other fields on the user instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Only set password if it's provided
        if password and password.strip():
            instance.set_password(password)
        
        instance.save()
        
        # Auto-create PupilProfile if role changed to pupil and profile doesn't exist
        if instance.role == 'pupil':
            profile, _ = PupilProfile.objects.get_or_create(user=instance)
            # If admin provided a pupil_class, set it on the profile
            if pupil_class is not None:
                try:
                    # Accept integer ID or string that can be cast to int
                    profile.pupil_class_id = int(pupil_class) if pupil_class != '' else None
                except Exception:
                    profile.pupil_class = profile.pupil_class
                profile.save()
        else:
            # If role is not pupil but an admin provided a pupil_class, ignore it
            pass
        
        return instance


class PupilProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for PupilProfile model
    """
    user = UserSerializer(read_only=True)
    class_name = serializers.CharField(source='pupil_class.name', read_only=True)
    
    class Meta:
        model = PupilProfile
        fields = ['id', 'user', 'pupil_class', 'class_name', 'admission_number', 
                  'date_of_birth', 'guardian_name', 'guardian_phone', 'address']


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login endpoint
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users (Admin only)
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    # Accept class id on create for pupils (write-only). Support legacy 'student_class' key too.
    pupil_class = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    student_class = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'full_name', 'role', 
                  'email', 'phone_number', 'profile_image', 'pupil_class', 'student_class']
        extra_kwargs = {
            'username': {'required': True},
            'full_name': {'required': True},
            'role': {'required': True},
            'email': {'required': False, 'allow_blank': True, 'allow_null': True}
        }
    
    def create(self, validated_data):
        # Extract optional class values (may be provided as legacy student_class or pupil_class)
        pupil_class = validated_data.pop('pupil_class', None)
        student_class = validated_data.pop('student_class', None)
        # prefer pupil_class if set, else student_class
        class_id = pupil_class if pupil_class is not None else student_class

        # Validate that pupils must have a class assigned
        role = validated_data.get('role')
        if role == 'pupil':
            # Convert empty string to None
            if class_id == '' or class_id == 'null' or class_id == 'undefined':
                class_id = None
            
            if not class_id:
                raise serializers.ValidationError({
                    'pupil_class': 'A class must be assigned for pupils.'
                })

        password = validated_data.pop('password')
        
        # Handle empty email - convert to None
        if 'email' in validated_data and not validated_data['email']:
            validated_data['email'] = None
        
        # Handle empty phone_number - convert to None
        if 'phone_number' in validated_data and not validated_data['phone_number']:
            validated_data['phone_number'] = None
        
        # Remove profile_image if it's None or empty string
        if 'profile_image' in validated_data and not validated_data.get('profile_image'):
            validated_data.pop('profile_image', None)
            
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Auto-create PupilProfile if role is pupil
        if user.role == 'pupil':
            profile = PupilProfile.objects.create(user=user)
            # set class if provided
            if class_id not in [None, '', 'null', 'undefined']:
                try:
                    profile.pupil_class_id = int(class_id)
                    profile.save()
                except (ValueError, TypeError) as e:
                    # If class assignment fails, delete the user and raise error
                    user.delete()
                    raise serializers.ValidationError({
                        'pupil_class': f'Invalid class ID provided: {str(e)}'
                    })
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile view
    """
    pupil_profile = PupilProfileSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'full_name', 'role', 'email', 'phone_number', 
                  'profile_image', 'pupil_profile', 'is_active']
        read_only_fields = ['id', 'username', 'role']
