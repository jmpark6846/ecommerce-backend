from rest_framework import serializers
from simple_history.models import HistoricalRecords

from payment.models import Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(read_only=True, many=True)
    order_log = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_order_log(self, obj):
        return get_change_from_histories(obj.order_log)


def serialize_change(history, change=None, created: bool=False):
    if history.history_user is None:
        history.history_user_id = history.instance
    HistoricalRecords
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
    class Meta:
        model = Payment
        fields = '__all__'
