from django.urls import path
from .views import FieldOwnerAPI
from .views import FieldOwnerLoginAPI,FieldOwnerGetMoneyAPI,FieldOwnerReportsAPI
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('register/',FieldOwnerAPI.as_view()),
    path('login/',FieldOwnerLoginAPI.as_view()),
    path("owner/money/", FieldOwnerGetMoneyAPI.as_view()),      # was owner/money/<int:owner_id>/
    path("owner/reports/", FieldOwnerReportsAPI.as_view()),     # was owner/reports/<int:owner_id>/
    path("token/refresh/", TokenRefreshView.as_view()),
    
]