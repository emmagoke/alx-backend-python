from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as JwtTokenObtainPairSerializer,
)


class CustomTokenObtainPairSerializer(JwtTokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)
        # Add custom claims
        token["user_id"] = str(user.user_id)  # Use str to ensure it's a string representation of UUID
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        # token["is_admin"] = user.is_admin
        # token["is_superuser"] = user.is_superuser

        return token
