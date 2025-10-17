from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserViewSet, PupilProfileViewSet, login_view, 
    register_view, profile_view, update_profile_view
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'pupil-profiles', PupilProfileViewSet, basename='pupil-profile')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_view, name='login'),
    path('auth/register/', register_view, name='register'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/profile/', profile_view, name='profile'),
    path('auth/profile/update/', update_profile_view, name='update_profile'),
]
