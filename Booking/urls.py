from django.urls import path
from .views import BookingAPI

urlpatterns = [
    path('getReservation/<int:field_id>/',BookingAPI.as_view()), # GET

]