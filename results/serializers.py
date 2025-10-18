from rest_framework import serializers
from .models import Result, AcademicSession, ResultSummary


class AcademicSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for AcademicSession model
    """
    current_term = serializers.CharField()
    
    class Meta:
        model = AcademicSession
        fields = ['id', 'name', 'start_date', 'end_date', 'is_active', 'result_release_date', 'current_term', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    # Removed get_current_term; now returns actual value


class ResultSerializer(serializers.ModelSerializer):
    """
    Serializer for Result model
    """
    pupil_name = serializers.CharField(source='pupil.full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    pupil_class = serializers.SerializerMethodField()
    
    class Meta:
        model = Result
        fields = ['id', 'pupil', 'pupil_name', 'pupil_class', 'subject', 'subject_name', 
                  'session', 'session_name', 'term', 'test_score', 'exam_score', 'total', 
                  'grade', 'teacher_comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total', 'grade', 'created_at', 'updated_at']
    
    def get_pupil_class(self, obj):
        try:
            return obj.pupil.pupil_profile.pupil_class.name
        except:
            return None
    
    def validate(self, attrs):
        # Ensure test_score is between 0 and 30
        if attrs.get('test_score') and (attrs['test_score'] < 0 or attrs['test_score'] > 30):
            raise serializers.ValidationError({"test_score": "Test score must be between 0 and 30"})
        
        # Ensure exam_score is between 0 and 70
        if attrs.get('exam_score') and (attrs['exam_score'] < 0 or attrs['exam_score'] > 70):
            raise serializers.ValidationError({"exam_score": "Exam score must be between 0 and 70"})
        
        return attrs


class ResultCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating results
    """
    class Meta:
        model = Result
        fields = ['pupil', 'subject', 'session', 'term', 'test_score', 'exam_score', 'teacher_comment']
    
    def validate_test_score(self, value):
        """Validate test score"""
        if value is None:
            raise serializers.ValidationError("Test score is required")
        if value < 0 or value > 30:
            raise serializers.ValidationError("Test score must be between 0 and 30")
        return value
    
    def validate_exam_score(self, value):
        """Validate exam score"""
        if value is None:
            raise serializers.ValidationError("Exam score is required")
        if value < 0 or value > 70:
            raise serializers.ValidationError("Exam score must be between 0 and 70")
        return value
    
    def validate(self, attrs):
        # Check all required fields
        required_fields = ['pupil', 'subject', 'session', 'term', 'test_score', 'exam_score']
        missing_fields = []
        
        for field in required_fields:
            if field not in attrs or attrs[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            raise serializers.ValidationError({
                'error': f"Missing required fields: {', '.join(missing_fields)}"
            })
        
        # Check for duplicate result
        if not self.instance:  # Only for create, not update
            existing = Result.objects.filter(
                pupil=attrs['pupil'],
                subject=attrs['subject'],
                session=attrs['session'],
                term=attrs['term']
            ).exists()
            
            if existing:
                raise serializers.ValidationError({
                    'error': 'A result already exists for this pupil, subject, session, and term combination.'
                })
        
        return attrs


class ResultSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for ResultSummary model
    """
    pupil_name = serializers.CharField(source='pupil.full_name', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    pupil_class = serializers.SerializerMethodField()
    results = serializers.SerializerMethodField()
    
    class Meta:
        model = ResultSummary
        fields = ['id', 'pupil', 'pupil_name', 'pupil_class', 'session', 'session_name', 
                  'term', 'total_subjects', 'total_score', 'average_score', 'overall_grade', 
                  'principal_comment', 'teacher_comment', 'results', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_subjects', 'total_score', 'average_score', 
                           'overall_grade', 'created_at', 'updated_at']
    
    def get_pupil_class(self, obj):
        try:
            return obj.pupil.pupil_profile.pupil_class.name
        except:
            return None
    
    def get_results(self, obj):
        results = Result.objects.filter(
            pupil=obj.pupil,
            session=obj.session,
            term=obj.term
        )
        return ResultSerializer(results, many=True).data


class BulkResultCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk result creation
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set subject queryset
        from classes.models import Subject
        self.fields['subject'] = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    
    session = serializers.PrimaryKeyRelatedField(queryset=AcademicSession.objects.all())
    term = serializers.ChoiceField(choices=Result.TERM_CHOICES)
    results = serializers.ListField(
        child=serializers.DictField()
    )
