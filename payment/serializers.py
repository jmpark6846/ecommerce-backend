from rest_framework import serializers
from simple_history.models import HistoricalRecords

from inventory.serializers import ProductOptionSerializer
from payment.models import Order, OrderItem, Payment


from inventory.models import ProductOption, Product, ShoppingCartItem, ShoppingCart
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


class OrderItemDetailSerializer(serializers.ModelSerializer):
    option = ProductOptionSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'option', 'qty', 'amount']

    def to_representation(self, instance):
        result = super(OrderItemDetailSerializer, self).to_representation(instance)
        result['option']['product'] = {"name": instance.option.product.name}
        return result


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ['id', 'total_amount', 'ordered_at', 'items', 'status']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(read_only=True, many=True)
    order_log = serializers.SerializerMethodField()
    products_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_amount', 'shipping_fee', 'ordered_at', 'order_log', 'products_amount',
                  'items']

    def get_order_log(self, obj):
        return get_change_from_histories(obj.order_log)

    def get_products_amount(self, obj):
        return obj.get_products_amount()


def serialize_change(history, change=None, created: bool = False):
    if history.history_user is None:
        history.history_user_id = history.instance

    if created:
        return {
            'field': None,
            'old_value': None,
            'new_value': None,
            'user': {'id': history.history_user.id, 'username': history.history_user.username},
            'type': history.history_type,
            'date': history.history_date,
        }
    else:
        return {
            'field': change.field,
            'user': {'id': history.history_user.id, 'username': history.history_user.username},
            'type': history.history_type,
            'date': history.history_date,
            'old': change.old,
            'new': change.new,
        }


def get_change_from_histories(histories):
    result = []
    for history in histories.all():

        if history.prev_record:
            delta = history.diff_against(history.prev_record)
            for change in delta.changes:
                result.append(serialize_change(history, change))
        else:
            result.append(serialize_change(history, created=True))

    return result


class PaymentSerializer(serializers.ModelSerializer):
    order = OrderDetailSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'
