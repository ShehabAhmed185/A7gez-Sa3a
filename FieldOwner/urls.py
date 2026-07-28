from django.urls import path
from .views import FieldOwnerAPI
from .views import FieldOwnerLoginAPI

urlpatterns = [
    path('register/',FieldOwnerAPI.as_view()),
    path('login/',FieldOwnerLoginAPI.as_view()),
]