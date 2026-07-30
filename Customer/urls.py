from django.urls import path
from .views import CustomerAPI,CustomerLoginAPI

urlpatterns = [
    path('register/',CustomerAPI.as_view()), # POST
    path('login/',CustomerLoginAPI.as_view()), # POST

]