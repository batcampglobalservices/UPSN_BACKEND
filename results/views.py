from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .models import Result, AcademicSession, ResultSummary
from .serializers import (
    ResultSerializer, ResultCreateSerializer, AcademicSessionSerializer,
    ResultSummarySerializer, BulkResultCreateSerializer
)
from accounts.permissions import IsAdmin, IsAdminOrTeacher, IsPupil
from .utils import generate_result_pdf


class AcademicSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AcademicSession CRUD operations
    """
    queryset = AcademicSession.objects.all()
    serializer_class = AcademicSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    @method_decorator(cache_page(300))  # Cache for 5 minutes
    def list(self, request, *args, **kwargs):
        """Cached list of academic sessions"""
        return super().list(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(300))  # Cache for 5 minutes
    def active(self, request):
        """Get the active academic session"""
        active_session = AcademicSession.objects.filter(is_active=True).first()
        if active_session:
            serializer = self.get_serializer(active_session)
            return Response(serializer.data)
        return Response({'error': 'No active session found'}, status=status.HTTP_404_NOT_FOUND)


class ResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Result CRUD operations
    Admin: Full access
    Teacher: Can create/edit results for their assigned classes
    Pupil: Read-only access to their own results
    """
    queryset = Result.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['pupil', 'subject', 'session', 'term', 'grade']
    search_fields = ['pupil__full_name', 'subject__name']
    ordering_fields = ['created_at', 'total']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return ResultCreateSerializer
        return ResultSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Optimize queries with select_related to prevent N+1 queries
        base_queryset = Result.objects.select_related(
            'pupil', 
            'subject', 
            'session',
            'pupil__pupil_profile',
            'pupil__pupil_profile__pupil_class'
        )
        
        if user.role == 'admin':
            return base_queryset.all()
        elif user.role == 'teacher':
            # Teachers can see results for pupils in their assigned classes
            from classes.models import Class
            teacher_classes = Class.objects.filter(assigned_teacher=user)
            return base_queryset.filter(
                pupil__pupil_profile__pupil_class__in=teacher_classes
            )
        elif user.role == 'pupil':
            # Pupils can only see their own results
            return base_queryset.filter(pupil=user)
        return Result.objects.none()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAdminOrTeacher()]
        elif self.action == 'destroy':
            return [IsAdmin()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """Create a new result and auto-generate summary"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"📝 Creating result with data: {request.data}")
        
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            logger.error(f"❌ Validation failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = serializer.save()
            logger.info(f"✅ Result created: Pupil {result.pupil.username}, Subject {result.subject.name}, Term {result.term}")
            
            # Auto-generate or update result summary for this pupil, session, and term
            self._update_result_summary(result.pupil, result.session, result.term)
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f"❌ Error creating result: {str(e)}")
            return Response({
                'error': 'Failed to create result',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Update result and regenerate summary"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        # Regenerate result summary
        self._update_result_summary(result.pupil, result.session, result.term)
        
        return Response(serializer.data)
    
    def _update_result_summary(self, pupil, session, term):
        """Generate or update result summary for a pupil"""
        summary, created = ResultSummary.objects.get_or_create(
            pupil=pupil,
            session=session,
            term=term
        )
        summary.calculate_summary()
        return summary
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple results at once and auto-generate summaries"""
        serializer = BulkResultCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        session = serializer.validated_data['session']
        term = serializer.validated_data['term']
        subject = serializer.validated_data['subject']
        results_data = serializer.validated_data['results']
        
        created_results = []
        errors = []
        pupils_to_update = set()
        
        for result_data in results_data:
            try:
                result, created = Result.objects.update_or_create(
                    pupil_id=result_data['pupil_id'],
                    subject=subject,
                    session=session,
                    term=term,
                    defaults={
                        'test_score': result_data['test_score'],
                        'exam_score': result_data['exam_score'],
                        'teacher_comment': result_data.get('teacher_comment', '')
                    }
                )
                created_results.append(result)
                pupils_to_update.add(result.pupil)
            except Exception as e:
                errors.append({
                    'pupil_id': result_data.get('pupil_id'),
                    'error': str(e)
                })
        
        # Auto-generate summaries for all affected pupils
        for pupil in pupils_to_update:
            self._update_result_summary(pupil, session, term)
        
        return Response({
            'message': f'{len(created_results)} results created/updated successfully',
            'created': len(created_results),
            'errors': errors,
            'summaries_updated': len(pupils_to_update)
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_results(self, request):
        """Get results for the logged-in pupil"""
        if request.user.role != 'pupil':
            return Response(
                {'error': 'This endpoint is only for pupils'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        session_id = request.query_params.get('session')
        term = request.query_params.get('term')
        
        # Optimized query with select_related
        results = Result.objects.filter(pupil=request.user).select_related(
            'subject', 'session'
        )
        
        if session_id:
            results = results.filter(session_id=session_id)
        if term:
            results = results.filter(term=term)
        
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)


class ResultSummaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ResultSummary operations
    """
    queryset = ResultSummary.objects.all()
    serializer_class = ResultSummarySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['pupil', 'session', 'term']
    
    def get_queryset(self):
        user = self.request.user
        # Optimize with select_related to prevent N+1 queries
        base_queryset = ResultSummary.objects.select_related(
            'pupil',
            'session',
            'pupil__pupil_profile',
            'pupil__pupil_profile__pupil_class'
        )
        
        if user.role == 'admin':
            return base_queryset.all()
        elif user.role == 'teacher':
            # Teachers can see summaries for pupils in their assigned classes
            from classes.models import Class
            teacher_classes = Class.objects.filter(assigned_teacher=user)
            return base_queryset.filter(
                pupil__pupil_profile__pupil_class__in=teacher_classes
            )
        elif user.role == 'pupil':
            return base_queryset.filter(pupil=user)
        return ResultSummary.objects.none()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'])
    def calculate(self, request, pk=None):
        """Recalculate summary from results"""
        summary = self.get_object()
        summary.calculate_summary()
        serializer = self.get_serializer(summary)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def pdf(self, request, pk=None):
        """Generate and download result PDF"""
        summary = self.get_object()
        
        # Generate PDF
        pdf_buffer = generate_result_pdf(summary)
        
        # Return PDF as response
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        filename = f"Result_{summary.pupil.username}_{summary.term}_{summary.session.name.replace('/', '-')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @action(detail=False, methods=['post'])
    def generate_summary(self, request):
        """Generate summary for a pupil, session, and term"""
        pupil_id = request.data.get('pupil')
        session_id = request.data.get('session')
        term = request.data.get('term')
        
        if not all([pupil_id, session_id, term]):
            return Response(
                {'error': 'pupil, session, and term are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        summary, created = ResultSummary.objects.get_or_create(
            pupil_id=pupil_id,
            session_id=session_id,
            term=term
        )
        
        summary.calculate_summary()
        serializer = self.get_serializer(summary)
        
        return Response({
            'message': 'Summary generated successfully',
            'summary': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

