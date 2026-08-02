from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ClubSerializer
from .models import Club, ClubImage
import random
import string
from rest_framework.parsers import MultiPartParser, FormParser
from FieldOwner.authentication import FieldOwnerJWTAuthentication


class ClubAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]
    authentication_classes = [FieldOwnerJWTAuthentication]
    permission_classes = [IsAuthenticated]

    # add new club to db
    def post(self, request):
        owner = request.user

        # Check if this owner already has a registered club
        if Club.objects.filter(owner_id=owner.id).exists():
            return Response({
                "success": False,
                "error": "This owner already has a registered club."
            }, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data["code"] = self.generate_club_code()

        serializer = ClubSerializer(data=data)

        if serializer.is_valid():
            club = serializer.save(owner_id=owner.id)

            images = request.FILES.getlist("images")

            for image in images:
                ClubImage.objects.create(
                    club=club,
                    image=image
                )

            return Response({
                "success": True,
                "message": "Club created successfully",
                "data": ClubSerializer(club).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_club_code(self):
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
            if not Club.objects.filter(code=code).exists():
                return code