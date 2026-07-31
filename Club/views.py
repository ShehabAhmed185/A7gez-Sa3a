from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ClubSerializer
from .models import Club, ClubImage
from FieldOwner.models import FieldOwner
import random
import string
from rest_framework.parsers import MultiPartParser, FormParser

class ClubAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]

    # add new club to db
    def post(self, request):
        # 1. Get owner_id sent from front-end body
        owner_id = request.data.get("owner_id")

        if not owner_id:
            return Response({
                "success": False,
                "error": "owner_id is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. Verify that the FieldOwner exists in DB
        if not FieldOwner.objects.filter(id=owner_id).exists():
            return Response({
                "success": False,
                "error": "Field owner with this ID does not exist."
            }, status=status.HTTP_404_NOT_FOUND)

        # 3. Check if this owner already has a registered club
        if Club.objects.filter(owner_id=owner_id).exists():
            return Response({
                "success": False,
                "error": "This owner already has a registered club."
            }, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data["code"] = self.generate_club_code()

        serializer = ClubSerializer(data=data)

        if serializer.is_valid():
            club = serializer.save(owner_id=owner_id)

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