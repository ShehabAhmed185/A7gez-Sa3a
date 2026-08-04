from decimal import Decimal, InvalidOperation, ROUND_DOWN

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.db.models import DecimalField, IntegerField, Value
from django.db.models.functions import Coalesce

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from .authentication import SuperAdminJWTAuthentication
from Booking.models import MoneyCalc
from FieldOwner.models import FieldOwner

from .models import SuperAdmin
from .serializers import SuperAdminSerializer




class SuperAdminAPI(APIView):
    # Register
    def post(self, request):
        serializer = SuperAdminSerializer(data=request.data)

        if serializer.is_valid():
            # Hash the password before saving
            serializer.save(
                password=make_password(serializer.validated_data["password"])
            )

            return Response(
                {
                    "success": True,
                    "message": "Super Admin registered successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class SuperAdminLoginAPI(APIView):
    # Login
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {
                    "success": False,
                    "message": "Username and password are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            admin = SuperAdmin.objects.get(username=username)
        except SuperAdmin.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Invalid username or password.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not check_password(password, admin.password):
            return Response(
                {
                    "success": False,
                    "message": "Invalid username or password.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Login successful — issue a JWT pair for this admin.
        # RefreshToken.for_user() only needs `admin.pk`, so this works
        # even though SuperAdmin isn't Django's AUTH_USER_MODEL.
        refresh = RefreshToken.for_user(admin)

        serializer = SuperAdminSerializer(admin)
        data = dict(serializer.data)
        data.pop("password", None)  # never echo the hash back
        data["access"] = str(refresh.access_token)
        data["refresh"] = str(refresh)

        return Response(
            {
                "success": True,
                "type":"Super Admin",
                "message": "Login successful.",
                "data": data,
            },
            status=status.HTTP_200_OK,
        )








class SuperAdminMoneyReportAPI(APIView):
    """
    GET /superadmin/getAllOwnersMoney/

    Returns a money report for every FieldOwner.
    Owners without a MoneyCalc record will have zero values.
    """
    authentication_classes = [SuperAdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        owners = (
            FieldOwner.objects
            .select_related("money_calc")
            .annotate(
                total_hours=Coalesce(
                    "money_calc__total_reserved_hours",
                    Value(0),
                    output_field=IntegerField(),
                ),
                rate_per_hour=Coalesce(
                    "money_calc__company_rate_per_hour",
                    Value(0),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
                total_money=Coalesce(
                    "money_calc__total_company_money",
                    Value(0),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
            )
            .order_by("-total_money")
        )

        data = []

        for owner in owners:
            try:
                updated_at = owner.money_calc.updated_at
            except MoneyCalc.DoesNotExist:
                updated_at = None

            data.append({
                "owner_id": owner.id,
                "owner_name": owner.name,
                "username": owner.username,
                "total_reserved_hours": owner.total_hours,
                "company_rate_per_hour": str(owner.rate_per_hour),
                "total_company_money": str(owner.total_money),
                "updated_at": updated_at,
            })

        grand_total = sum(
            (owner.total_money for owner in owners),
            start=Decimal("0.00")
        )

        return Response(
            {
                "success": True,
                "message": "Money report fetched successfully.",
                "count": len(data),
                "grand_total_company_money": str(grand_total),
                "data": data,
            },
            status=status.HTTP_200_OK,
        )



class SuperAdminMoneyDecreaseAPI(APIView):
    """
    POST /api/super-admin/owners/<owner_id>/money-decrease/
    Body: { "amount": "150.00" }

    Decreases total_company_money by `amount`, and decreases
    total_reserved_hours by (amount / company_rate_per_hour),
    rounded down to the nearest whole hour.
    """
    authentication_classes = [SuperAdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, owner_id):
        raw_amount = request.data.get("amount")

        if raw_amount in (None, ""):
            return Response(
                {"success": False, "message": "amount is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = Decimal(str(raw_amount))
        except InvalidOperation:
            return Response(
                {"success": False, "message": "amount must be a valid number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if amount <= 0:
            return Response(
                {"success": False, "message": "amount must be greater than 0."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            try:
                money_calc = (
                    MoneyCalc.objects
                    .select_for_update()
                    .get(owner_id=owner_id)
                )
            except MoneyCalc.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "message": f"No MoneyCalc record found for owner_id={owner_id}.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if money_calc.company_rate_per_hour <= 0:
                return Response(
                    {
                        "success": False,
                        "message": "company_rate_per_hour is 0; cannot derive hours from amount.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if amount > money_calc.total_company_money:
                return Response(
                    {
                        "success": False,
                        "message": "amount exceeds current total_company_money.",
                        "current_total_company_money": str(money_calc.total_company_money),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # hours to subtract, rounded down to a whole hour
            hours_to_subtract = int(
                (amount / money_calc.company_rate_per_hour).to_integral_value(rounding=ROUND_DOWN)
            )

            if hours_to_subtract > money_calc.total_reserved_hours:
                return Response(
                    {
                        "success": False,
                        "message": "Derived hours exceed current total_reserved_hours.",
                        "current_total_reserved_hours": money_calc.total_reserved_hours,
                        "derived_hours_to_subtract": hours_to_subtract,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            money_calc.total_company_money -= amount
            money_calc.total_reserved_hours -= hours_to_subtract
            money_calc.save(update_fields=["total_company_money", "total_reserved_hours", "updated_at"])

        return Response(
            {
                "success": True,
                "message": "Money and hours decreased successfully.",
                "data": {
                    "owner_id": money_calc.owner_id,
                    "amount_deducted": str(amount),
                    "hours_deducted": hours_to_subtract,
                    "total_reserved_hours": money_calc.total_reserved_hours,
                    "company_rate_per_hour": str(money_calc.company_rate_per_hour),
                    "total_company_money": str(money_calc.total_company_money),
                    "updated_at": money_calc.updated_at,
                },
            },
            status=status.HTTP_200_OK,
        )





class DeleteFieldOwnerAPI(APIView):
    authentication_classes = [SuperAdminJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, owner_id):
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

        owner_name = owner.name
        owner.delete()

        return Response(
            {
                "success": True,
                "message": f"Field owner '{owner_name}' and all related data deleted successfully."
            },
            status=status.HTTP_200_OK
        )