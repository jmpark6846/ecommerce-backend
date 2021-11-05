from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from inventory.models import Product, ProductReview
from ecommerce.permissions import IsAuthor
from inventory.serializers import ProductReviewSerializer, ProductListSerializer, \
    ProductDetailSerializer


class ProductViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.action in ['list']:
            serializer_class = ProductListSerializer
        elif self.action in ['retrieve', 'create', ]:
            serializer_class = ProductDetailSerializer
        else:
            serializer_class = ProductDetailSerializer

        return serializer_class

    def get_serializer_context(self):
        context = super(ProductViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context


class ProductReviewViewSet(ModelViewSet):
    serializer_class = ProductReviewSerializer

    def get_permissions(self):
        if self.action in ['list']:
            permission_classes = []
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated]  # 상품을 산 사람만
        elif self.action in ['update', 'destroy']:
            permission_classes = [IsAuthor, IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return ProductReview.objects.filter(author=self.request.user, product_id=self.kwargs['product_pk'])
