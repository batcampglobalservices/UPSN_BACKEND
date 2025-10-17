from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResultViewSet, AcademicSessionViewSet, ResultSummaryViewSet

router = DefaultRouter()
router.register(r'results', ResultViewSet, basename='result')
router.register(r'sessions', AcademicSessionViewSet, basename='session')
router.register(r'summaries', ResultSummaryViewSet, basename='summary')

urlpatterns = [
    path('', include(router.urls)),
]
