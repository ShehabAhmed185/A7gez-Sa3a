from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerSerializer,CustomerLoginSerializer
from .models import Customer


class CustomerAPI(APIView):
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response(
                {
                    "message": "Customer registered successfully.",
                    "customer": {
                        "id": customer.id,
                        "name": customer.name,
                        "username": customer.username,
                        "email": customer.email,
                        "zone": customer.zone,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CustomerLoginAPI(APIView):
    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.validated_data['customer']
            return Response(
                {
                    "message": "Login successful.",
                    "customer": {
                        "id": customer.id,
                        "name": customer.name,
                        "username": customer.username,
                        "email": customer.email,
                        "zone": customer.zone,
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        # {
        #     "username": "johndoe123",
        #     "password": "SecurePass123"
        # }