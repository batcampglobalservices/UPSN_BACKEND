from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarouselImageViewSet, SchoolLogoViewSet

router = DefaultRouter()
router.register(r'carousel', CarouselImageViewSet, basename='carousel')
router.register(r'logo', SchoolLogoViewSet, basename='logo')

urlpatterns = [
    path('', include(router.urls)),
]
