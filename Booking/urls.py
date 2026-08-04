from django.urls import path
from .views import BookingAPI

urlpatterns = [
    path('reservation/<int:field_id>/',BookingAPI.as_view()), # GET

]