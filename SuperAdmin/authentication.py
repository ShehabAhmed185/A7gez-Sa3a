from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

from .models import SuperAdmin


class SuperAdminJWTAuthentication(JWTAuthentication):
    """
    JWT authentication for SuperAdmin.

    SuperAdmin is not Django's AUTH_USER_MODEL, so we can't rely on
    JWTAuthentication's default get_user(), which looks the user up in
    the configured user model. Instead we validate the token the same
    way (raises on missing/invalid/expired token), then resolve the
    SuperAdmin ourselves from the "user_id" claim that
    RefreshToken.for_user(admin) embeds automatically.
    """

    def get_user(self, validated_token):
        user_id = validated_token.get("user_id")

        if user_id is None:
            raise AuthenticationFailed("Token contained no recognizable user identification.")

        try:
            admin = SuperAdmin.objects.get(id=user_id)
        except SuperAdmin.DoesNotExist:
            raise AuthenticationFailed("Super Admin not found.")

        return admin