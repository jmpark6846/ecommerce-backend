from rest_framework import serializers

from accounts.models import User
from payment.serializers import ShoppingCartSerializer


class UserDetailSerializer(serializers.ModelSerializer):
    shoppingcart = ShoppingCartSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['pk', 'email', 'username', 'is_staff', 'is_active', 'date_joined', 'last_login', 'shoppingcart']
