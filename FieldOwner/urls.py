from django.urls import path
from .views import FieldOwnerAPI
from .views import FieldOwnerLoginAPI,FieldOwnerGetMoneyAPI,FieldOwnerReportsAPI

urlpatterns = [
    path('register/',FieldOwnerAPI.as_view()),
    path('login/',FieldOwnerLoginAPI.as_view()),
    path('getMoney/<int:owner_id>/',FieldOwnerGetMoneyAPI.as_view()),
    path('getReport/<int:owner_id>/',FieldOwnerReportsAPI.as_view()),
]