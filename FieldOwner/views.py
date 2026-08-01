from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FieldOwnerSerializer
from django.contrib.auth.hashers import check_password
from .models import FieldOwner
from Booking.models import MoneyCalc,Booking
class FieldOwnerAPI(APIView):

    def get(self, request):
        owners = FieldOwner.objects.all()
        serializer = FieldOwnerSerializer(owners, many=True)

        return Response(
            {
                "success": True,
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


    def post(self, request):
        serializer = FieldOwnerSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Registration successful",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class FieldOwnerLoginAPI(APIView):

    def post(self, request):
        #  "username": "ahmed_owner",
        #  "password": "Ahmed@123",
        username = request.data.get("username")
        password = request.data.get("password")

        # Check if both fields are provided
        if not username or not password:
            return Response(
                {
                    "success": False,
                    "message": "Username and password are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find the user
        try:
            owner = FieldOwner.objects.get(username=username)
        except FieldOwner.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Invalid username or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Verify password
        if not check_password(password, owner.password):
            return Response(
                {
                    "success": False,
                    "message": "Invalid username or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Login successful
        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "data": {
                    "id": owner.id,
                    "name": owner.name,
                    "username": owner.username,
                    "email": owner.email,
                    "phone_number": owner.phone_number
                }
            },
            status=status.HTTP_200_OK
        )




class FieldOwnerGetMoneyAPI(APIView):

    def get(self, request, owner_id):
        # 1. Verify the owner exists
        try:
            owner = FieldOwner.objects.get(id=owner_id)
        except FieldOwner.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Field owner not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Fetch this owner's money calculation record
        money_calc = MoneyCalc.objects.filter(owner=owner).first()

        if not money_calc:
            return Response(
                {
                    "success": True,
                    "message": "No reservations recorded yet for this owner.",
                    "data": {
                        "owner_id": owner.id,
                        "owner_name": owner.name,
                        "total_reserved_hours": 0,
                        "company_rate_per_hour": 0,
                        "total_company_money": 0,
                    }
                },
                status=status.HTTP_200_OK
            )

        # 3. Return the report
        return Response(
            {
                "success": True,
                "data": {
                    "owner_id": owner.id,
                    "owner_name": owner.name,
                    "total_reserved_hours": money_calc.total_reserved_hours,
                    "company_rate_per_hour": money_calc.company_rate_per_hour,
                    "total_company_money": money_calc.total_company_money,
                    "updated_at": money_calc.updated_at,
                }
            },
            status=status.HTTP_200_OK
        )


class FieldOwnerReportsAPI(APIView):

    def get(self, request, owner_id):
        # 1. Verify the owner exists
        try:
            owner = FieldOwner.objects.get(id=owner_id)
        except FieldOwner.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Field owner not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Get all bookings for fields belonging to this owner's clubs
        bookings = (
            Booking.objects.filter(field__club__owner_id=owner_id)
            .select_related("field", "field__club")
            .order_by("-date")
        )

        # 3. Build the response data
        data = [
            {
                "booking_id": booking.id,
                "field_id": booking.field_id,
                "field_name": booking.field.field_name,
                "club_name": booking.field.club.title,
                "date": str(booking.date),
                "reservation_code": booking.reservationCode,
                "reserved_hours": booking.reserved_hours,
                "created_at": booking.created_at,
            }
            for booking in bookings
        ]

        return Response(
            {
                "success": True,
                "owner_id": owner.id,
                "owner_name": owner.name,
                "total_bookings": len(data),
                "data": data,
            },
            status=status.HTTP_200_OK
        )