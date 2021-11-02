from rest_framework import serializers

from inventory.models import Product, ProductReview, ProductOption


class ProductOptionSerialiezr(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = '__all__'


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    options = ProductOptionSerialiezr(read_only=True)
    reviews = ProductReviewSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

