from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework_simplejwt.settings import api_settings

from .models import FieldOwner


class FieldOwnerJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication for the FieldOwner model.

    SimpleJWT's default JWTAuthentication.get_user() calls
    django.contrib.auth.get_user_model() to resolve the user_id claim.
    FieldOwner is NOT Django's AUTH_USER_MODEL (it doesn't inherit from
    AbstractBaseUser), so we override get_user() to look the id up in
    FieldOwner directly, instead of migrating the whole project's user
    model.
    """

    def get_user(self, validated_token):
        try:
            owner_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken("Token contained no recognizable user identification")

        try:
            owner = FieldOwner.objects.get(id=owner_id)
        except FieldOwner.DoesNotExist:
            raise AuthenticationFailed("Field owner not found", code="user_not_found")

        # DRF's IsAuthenticated permission (and other permission classes)
        # check `request.user.is_authenticated`. FieldOwner doesn't define
        # this attribute since it isn't a Django auth user, so we set it
        # explicitly on the resolved instance for this request.
        owner.is_authenticated = True

        return owner