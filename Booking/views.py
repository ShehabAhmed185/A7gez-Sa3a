from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Booking,MoneyCalc
from FiveSideFootball.models import Field  # Adjust path if needed
import random
import string
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response


class BookingAPI(APIView):
    def get(self, request, field_id):
    # 1. Check if field exists
        if not Field.objects.filter(id=field_id).exists():
            return Response(
                {"error": "Field not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # 2. Extract date from query parameters or default to today
        date_param = request.query_params.get("date")

        if date_param:
            try:
                target_date = datetime.strptime(date_param, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use 'YYYY-MM-DD'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            target_date = timezone.now().date()

        # 3. Get booking for the specified date
        booking = Booking.objects.filter(
            field_id=field_id, date=target_date
        ).first()

        # 4. Extract reserved hours
        reserved_hours = booking.reserved_hours if booking else []

        return Response(
            {
                "success": True,
                "field_id": field_id,
                "date": str(target_date),
                "reserved_hours": reserved_hours,
            },
            status=status.HTTP_200_OK,
        )


# Reserve field for a specific day and hour
    def post(self, request, field_id):
        # 1. Verify if the Field exists
        field = Field.objects.filter(id=field_id).first()
        if not field:
            return Response(
                {"error": "Field not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # 2. Extract hour and date from request body
        hour = request.data.get("hour")
        booking_date_str = request.data.get("date")  # Expected format: "YYYY-MM-DD"

        if hour is None or booking_date_str is None:
            return Response(
                {"error": "'hour' and 'date' fields are required in request body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate hour format (0-23)
        try:
            hour = int(hour)
            if not (0 <= hour <= 23):
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "Hour must be an integer between 0 and 23."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate date format (YYYY-MM-DD) and check if it's in the past
        try:
            booking_date = datetime.strptime(booking_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Date must be in 'YYYY-MM-DD' format."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if booking_date < timezone.now().date():
            return Response(
                {"error": "Cannot reserve field for a past date."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Use an atomic transaction to handle concurrent reservations safely
        with transaction.atomic():
            # Fetch existing booking record for the specific date with a lock
            booking = (
                Booking.objects.select_for_update()
                .filter(field=field, date=booking_date)
                .first()
            )

            if not booking:
                # Create a new booking for this date
                code = self.generate_reservation_code()
                booking = Booking.objects.create(
                    field=field,
                    date=booking_date,
                    reservationCode=code,
                    reserved_hours=[],
                )

            # 4. Check if the requested hour is already reserved
            if hour in booking.reserved_hours:
                return Response(
                    {
                        "error": f"Hour {hour}:00 is already reserved for {booking_date}."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Ensure reservation code exists
            if not booking.reservationCode:
                booking.reservationCode = self.generate_reservation_code()

            # 5. Save the updated reservation
            booking.reserved_hours.append(hour)
            booking.reserved_hours.sort()
            booking.save()

            owner = field.club.owner
            money_calc, _ = MoneyCalc.objects.get_or_create(owner=owner)
            # Use this field's actual hourly rate so the money calculation
            # is correct even if different fields charge different rates.
            money_calc.add_reservation(hours_count=1, rate_per_hour=field.hour_rate)

        # 6. Return response
        return Response(
            {
                "success": True,
                "message": f"Hour {hour}:00 successfully reserved for {booking_date}.",
                "reservation_code": booking.reservationCode,
                "field_id": field_id,
                "date": str(booking_date),
                "reserved_hours": booking.reserved_hours,
            },
            status=status.HTTP_201_CREATED,
        )

    def generate_reservation_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
            if not Booking.objects.filter(reservationCode=code).exists():
                return code