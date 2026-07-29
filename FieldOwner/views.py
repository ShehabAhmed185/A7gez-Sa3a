from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FieldOwnerSerializer
from django.contrib.auth.hashers import check_password
from .models import FieldOwner

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