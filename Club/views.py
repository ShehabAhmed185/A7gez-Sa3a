from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ClubSerializer
from .models import Club, ClubImage
import random
import string
from rest_framework.parsers import MultiPartParser, FormParser

class ClubAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]
    #add new club to db
    def post(self, request):
     
        data = request.data.copy()
        data["code"] = self.generate_club_code()

        serializer = ClubSerializer(data=data)

        if serializer.is_valid():
            club = serializer.save(owner_id=1) #i use owner_id =1 constant untill make it owner id from jwt

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