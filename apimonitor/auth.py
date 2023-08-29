import base64
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework.throttling import BaseThrottle

prefix = "THROTTLE_"


class HerconomyAPIAuthentication(BaseAuthentication):
    www_authenticate_realm = "api"

    def get_authorization_header(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        return auth

    def authenticate(self, request):
        auth = self.get_authorization_header(request).split()

        if not auth or auth[0].lower() != "basic":
            return None

        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(
                "Invalid basic header. No credentials provided."
            )
        if len(auth) > 2:
            raise exceptions.AuthenticationFailed(
                "Invalid basic header. Credential string is not properly formatted"
            )
        try:
            auth_decoded = base64.b64decode(auth[1]).decode("utf-8")
            username, password = auth_decoded.split(":")
        except (UnicodeDecodeError, ValueError):
            raise exceptions.AuthenticationFailed(
                "Invalid basic header. Credentials not correctly encoded"
            )

        return self.authenticate_credentials(username, password, request)

    def authenticate_credentials(self, username, password, request=None):
        credentials = {get_user_model().USERNAME_FIELD: username, "password": password}

        user = authenticate(request=request, **credentials)

        if user is None:
            raise exceptions.AuthenticationFailed("Invalid username or password")

        if not user.is_active:
            raise exceptions.AuthenticationFailed("User is inactive")

        return user, None


class MessageRequestThrotlle(BaseThrottle):
    def allow_request(self, request, view):
        _from = request.data.get("from")
        if cache.get(prefix + _from) is not None:
            count = cache.get(prefix + _from).get("count")
            if count == 50:
                return False
        return True
