from rest_framework import serializers

from inventory.models import ProductOption
from inventory.serializers import ProductOptionDetailSerializer


class TopSellingItemsSerializers(serializers.Serializer):
    option = serializers.IntegerField()
    total_amount = serializers.IntegerField()
    total_qty = serializers.IntegerField()

    def to_representation(self, instance):
        result = super(TopSellingItemsSerializers, self).to_representation(instance)
        option = ProductOption.objects.get(id=result['option'])
        result['option'] = ProductOptionDetailSerializer(option, context=self.context).data
        return result

