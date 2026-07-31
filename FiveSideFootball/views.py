from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FieldSerializer
from .models import Field
import random
import string
from FieldOwner.models import FieldOwner
from Club.models import Club

class FieldAPI(APIView):

    def generate_field_code(self):
        """Generate a unique 7-character code for a Field."""
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
            if not Field.objects.filter(code=code).exists():
                return code

    # add field to DB
    def post(self, request):
        data = request.data.copy()

        # Club id is constant = 11 untill use jwt
        data['club'] = 11

        # Auto-generate a unique code if the client didn't provide one
        if not data.get('code'):
            data['code'] = self.generate_field_code()

        serializer = FieldSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    #get fields related to ownerId and owner club
    def get(self, request, fieldOwner_id):
        if not FieldOwner.objects.filter(id=fieldOwner_id).exists():
            return Response(
                {"error": "Owner not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        fields = Field.objects.filter(club__owner_id=fieldOwner_id)
        if not fields.exists():
            return Response(
                {"error": "No fields found for this owner"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FieldSerializer(fields, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)