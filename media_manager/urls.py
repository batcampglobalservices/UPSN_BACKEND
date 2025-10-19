from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CarouselImageViewSet, SchoolLogoViewSet, SiteSettingViewSet

router = DefaultRouter()
router.register(r'carousel', CarouselImageViewSet, basename='carousel')
router.register(r'logo', SchoolLogoViewSet, basename='logo')
router.register(r'settings', SiteSettingViewSet, basename='settings')

urlpatterns = [
    path('', include(router.urls)),
]
