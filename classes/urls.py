from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassViewSet, SubjectViewSet

router = DefaultRouter()
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'subjects', SubjectViewSet, basename='subject')

urlpatterns = [
    path('', include(router.urls)),
]
