from django.urls import path, include
from accounts.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'inventory', InventoryViewSet, basename='inventory')


urlpatterns = [
    path('', include(router.urls)),
    path('register', RegistrationAPI.as_view()),
    path('invite_user', InvitedUserViewSet.as_view()),
    path('login', UserLoginAPI.as_view()),
    path('password/change', PasswordChangeAPI.as_view()),
]