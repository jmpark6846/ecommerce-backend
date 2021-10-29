from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from dj_rest_auth.jwt_auth import unset_jwt_cookies

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from dj_rest_auth.views import LogoutView as dj_rest_auth_LogoutView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutView(dj_rest_auth_LogoutView):
    def logout(self, request: Request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        response = Response(
            {'detail': 'Successfully logged out.'},
            status=status.HTTP_200_OK,
        )
        try:
            refresh = request.COOKIES['refresh']
        except KeyError:
            response.data = {'detail': _('Refresh token was not included in cookie.')}
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return response

        unset_jwt_cookies(response)

        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except (TokenError, AttributeError, TypeError) as error:
            if hasattr(error, 'args'):
                if 'Token is blacklisted' in error.args or 'Token is invalid or expired' in error.args:
                    response.data = {'detail': _(error.args[0])}
                    response.status_code = status.HTTP_401_UNAUTHORIZED
                else:
                    response.data = {'detail': _('An error has occurred.')}
                    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

            else:
                response.data = {'detail': _('An error has occurred.')}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return response


NOTIFICATION_MAX = 10
