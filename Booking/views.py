from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Booking
from FiveSideFootball.models import Field  # Adjust path if needed
import random
import string

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

    def post(self, request, field_id):
        # 1. Verify if the Field exists
        field = Field.objects.filter(id=field_id).first()
        if not field:
            return Response(
                {"error": "Field not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Extract requested hour slot from request body
        hour = request.data.get("hour")

        # Validate that hour is provided
        if hour is None:
            return Response(
                {"error": "'hour' field is required in request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure hour is an integer between 0 and 23
        try:
            hour = int(hour)
            if not (0 <= hour <= 23):
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "Hour must be an integer between 0 and 23."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Get today's date
        today = timezone.now().date()

        # 4. Fetch existing booking or get a new instance
        booking = Booking.objects.filter(field=field, date=today).first()

        if not booking:
            # Create a new booking with a unique reservation code
            code = self.generate_reservation_code()
            booking = Booking.objects.create(
                field=field,
                date=today,
                reservationCode=code,
                reserved_hours=[]
            )

        # 5. Check if the hour is already reserved
        if hour in booking.reserved_hours:
            return Response(
                {
                    "error": f"Hour {hour}:00 is already reserved for today."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ensure reservationCode exists if it wasn't populated previously
        if not booking.reservationCode:
            booking.reservationCode = self.generate_reservation_code()

        # 6. Append the new hour and keep the list sorted
        booking.reserved_hours.append(hour)
        booking.reserved_hours.sort()
        booking.save()

        # 7. Return response including reservationCode
        return Response(
            {
                "success": True,
                "message": f"Hour {hour}:00 successfully reserved for today.",
                "reservation_code": booking.reservationCode,
                "field_id": field_id,
                "date": today,
                "reserved_hours": booking.reserved_hours
            },
            status=status.HTTP_201_CREATED
        )

    def generate_reservation_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
            if not Booking.objects.filter(reservationCode=code).exists():
                return code