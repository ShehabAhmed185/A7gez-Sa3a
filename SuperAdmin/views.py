from django.contrib.auth.hashers import check_password, make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SuperAdminSerializer
from .models import SuperAdmin


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

        if check_password(password, admin.password):
            serializer = SuperAdminSerializer(admin)

            return Response(
                {
                    "success": True,
                    "message": "Login successful.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Invalid username or password.",
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )