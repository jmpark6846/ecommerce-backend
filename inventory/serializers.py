from rest_framework import serializers

from inventory.models import Product, ProductReview, ProductOption, ProductImage, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductOptionDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductOption
        fields = ['id', 'product', 'name', 'value', 'price', 'is_default', 'image']
        depth = 1

    def get_image(self, obj: ProductOption):
        product_image = obj.product.productimage_set.first()
        return ProductImageSerializer(product_image, context=self.context).data


class ProductOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOption
        fields = ['id', 'product', 'name', 'value', 'price', 'is_default']


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(use_url=True)

    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'price', 'image']

    def get_image(self, obj: Product):
        product_image = obj.productimage_set.first()
        return ProductImageSerializer(product_image, context=self.context).data


class ProductDetailSerializer(serializers.ModelSerializer):
    productimage_set = ProductImageSerializer(read_only=True, many=True)
    productoption_set = ProductOptionSerializer(read_only=True, many=True)
    reviews = ProductReviewSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'productoption_set', 'reviews', 'price', 'category', 'productimage_set', 'shipping_fee']
