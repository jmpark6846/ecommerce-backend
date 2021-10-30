from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ViewSetMixin, GenericViewSet

from inventory.models import Product, ProductReview
from inventory.permissions import IsAuthor
from inventory.serializers import ProductSerializer, ProductReviewSerializer


class ProductViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ProductReviewViewSet(ModelViewSet):
    serializer_class = ProductReviewSerializer

    def get_permissions(self):
        if self.action in ['list']:
            permission_classes = []
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated]  # 상품을 산 사람만
        elif self.action in ['update', 'delete']:
            permission_classes = [IsAuthor]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return ProductReview.objects.filter(author=self.request.user, product_id=self.kwargs['product_pk'])
