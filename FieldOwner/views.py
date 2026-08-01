from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import FieldOwnerSerializer
from django.contrib.auth.hashers import check_password
from .models import FieldOwner
from .authentication import FieldOwnerJWTAuthentication
from Booking.models import MoneyCalc, Booking


class FieldOwnerAPI(APIView):
    # NOTE: left unauthenticated on purpose.
    # POST is the public registration endpoint (an owner has no token
    # until they exist), and GET lists all owners rather than a specific
    # one, so there's no owner_id to swap for request.user. If you want
    # this list restricted to logged-in owners (or admins only), tell me
    # and I'll add authentication_classes/permission_classes here too.

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
    # No authentication_classes/permission_classes here either — a user
    # who doesn't have a token yet is exactly who needs to hit /login.

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

        # Login successful — issue a JWT pair for this owner.
        # RefreshToken.for_user() only needs `owner.pk`, so this works
        # even though FieldOwner isn't Django's AUTH_USER_MODEL.
        refresh = RefreshToken.for_user(owner)

        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "data": {
                    "id": owner.id,
                    "name": owner.name,
                    "username": owner.username,
                    "email": owner.email,
                    "phone_number": owner.phone_number,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            },
            status=status.HTTP_200_OK
        )


class FieldOwnerGetMoneyAPI(APIView):
    authentication_classes = [FieldOwnerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    # owner_id removed from the signature/URL: the owner is now taken
    # from the validated JWT (request.user), so an authenticated owner
    # can only ever see their own money report, not anyone else's by id.
    def get(self, request):
        owner = request.user

        # 1. Fetch this owner's money calculation record
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

        # 2. Return the report
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
    authentication_classes = [FieldOwnerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    # owner_id removed from the signature/URL for the same reason as
    # above — reports are scoped to the authenticated owner only.
    def get(self, request):
        owner = request.user

        # 1. Get all bookings for fields belonging to this owner's clubs
        bookings = (
            Booking.objects.filter(field__club__owner_id=owner.id)
            .select_related("field", "field__club")
            .order_by("-date")
        )

        # 2. Build the response data
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