from django.urls import path
from .views import SuperAdminLoginAPI,SuperAdminAPI
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path("register/", SuperAdminAPI.as_view()),     # was owner/reports/<int:owner_id>/
    path("login/", SuperAdminLoginAPI.as_view()),     # was owner/reports/<int:owner_id>/
    path("token/refresh/", TokenRefreshView.as_view()),
    
]