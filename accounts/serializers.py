from rest_framework import serializers

from accounts.models import User, ShoppingCart, ShoppingCartItem


class ShoppingCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCartItem
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):
    items = ShoppingCartItemSerializer(read_only=True, many=True)

    class Meta:
        model = ShoppingCart
        fields = ['user', 'items']


class UserDetailSerializer(serializers.ModelSerializer):
    shoppingcart = ShoppingCartSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['pk', 'email', 'username', 'is_staff', 'is_active', 'date_joined', 'last_login', 'shoppingcart']
