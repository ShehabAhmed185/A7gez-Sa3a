from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Booking
from FiveSideFootball.models import Field  # Adjust path if needed

class BookingAPI(APIView):
    def get(self, request, field_id):
        # 1. Check if field exists
        if not Field.objects.filter(id=field_id).exists():
            return Response(
                {"error": "Field not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Get today's date directly from Django (uses your TIME_ZONE setting)
        today = timezone.now().date()

        # 3. Get booking for today
        booking = Booking.objects.filter(field_id=field_id, date=today).first()

        # 4. If no booking record exists for today, reserved_hours is empty []
        reserved_hours = booking.reserved_hours if booking else []

        return Response(
            {
                "success": True,
                "field_id": field_id,
                "date": today,
                "reserved_hours": reserved_hours
            },
            status=status.HTTP_200_OK
        )