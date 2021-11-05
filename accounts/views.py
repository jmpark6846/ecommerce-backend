from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from dj_rest_auth.jwt_auth import unset_jwt_cookies

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from dj_rest_auth.views import LogoutView as dj_rest_auth_LogoutView
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import ShoppingCartItem
from accounts.serializers import ShoppingCartItemSerializer
from ecommerce.permissions import IsOwner
from payment.models import Order, OrderItem
from payment.serializers import OrderDetailSerializer


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


class CartView(APIView):
    permission_classes = [IsOwner, IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = ShoppingCartItem.objects.filter(cart=self.request.user.shoppingcart)
        serializer = ShoppingCartItemSerializer(qs, context={'request': request}, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        serializer = ShoppingCartItemSerializer(data=request.data['items'], context={'cart': request.user.shoppingcart},
                                                many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def delete(self, request, *args, **kwargs):
        qs = ShoppingCartItem.objects.filter(id__in=request.data['items'])
        qs.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckoutView(APIView):
    permission_classes = [IsOwner, IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart_items: [ShoppingCartItem] = self.request.user.shoppingcart.items.all()
        order = Order.objects.create(user=self.request.user)

        if cart_items.count() == 0:
            return Response({'error': '장바구니가 비어있습니다.'}, status=400)

        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                option=cart_item.option,
                qty=cart_item.qty,
            )

        return Response({'order': OrderDetailSerializer(order).data}, status=201)
