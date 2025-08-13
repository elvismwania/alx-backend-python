from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    """
    This can be extended in the future for additional custom auth logic.
    For now, it's a direct subclass of JWTAuthentication.
    """
    pass
