from rest_framework import serializers

from accounts.models import User, ShoppingCart, ShoppingCartItem
from inventory.models import ProductOption, Product
from inventory.serializers import ProductImageSerializer, ProductOptionSerializer


class ShoppingCartItemSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCartItem
        fields = ['cart', 'option', 'qty', 'product_image', 'id']
        # depth = 2

    def to_representation(self, instance):
        result = super(ShoppingCartItemSerializer, self).to_representation(instance)
        option = ProductOption.objects.get(id=result['option'])
        result['option'] = ProductOptionSerializer(option).data
        product = Product.objects.get(id=result['option']['product'])
        result['option']['product'] = {
            'id': product.id,
            'name': product.name,
        }
        return result

    def get_product_image(self, obj: ShoppingCartItem):
        product_image = obj.option.product.productimage_set.first()
        return ProductImageSerializer(product_image, context=self.context).data

    def create(self, validated_data):
        # product option이 겹치면 장바구니 항목을 생성하지 않고 기존항목의 수량을 증가시킴
        try:
            user_cart = self.context.get('cart')
            item = ShoppingCartItem.objects.get(option=validated_data['option'],
                                                cart=user_cart)
            item.qty += 1
            item.save()
            return item
        except ShoppingCartItem.DoesNotExist:
            return ShoppingCartItem.objects.create(**validated_data)


class ShoppingCartSerializer(serializers.ModelSerializer):
    items = ShoppingCartItemSerializer(read_only=True, many=True)

    class Meta:
        model = ShoppingCart
        fields = ['user', 'items', 'id']


class UserDetailSerializer(serializers.ModelSerializer):
    shoppingcart = ShoppingCartSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['pk', 'email', 'username', 'is_staff', 'is_active', 'date_joined', 'last_login', 'shoppingcart']
