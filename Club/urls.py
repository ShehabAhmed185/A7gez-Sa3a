from django.urls import path
from .views import ClubAPI

urlpatterns = [
    path('addClub/',ClubAPI.as_view()),
]