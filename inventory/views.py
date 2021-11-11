from django.contrib.postgres.search import SearchVector
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from ecommerce.pagination import DefaultPagination
from inventory.models import Product, ProductReview, Category
from ecommerce.permissions import IsAuthor
from inventory.serializers import ProductReviewSerializer, ProductListSerializer, \
    ProductDetailSerializer, CategorySerializer


class ProductViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Product.objects.order_by('-created_at')
    pagination_class = DefaultPagination

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

    def list(self, request, *args, **kwargs):
        search_term = request.query_params.get('search')
        if search_term:
            qs = Product.objects.filter(name__contains=search_term)
            page = self.paginate_queryset(qs)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        elif 'category' in request.query_params:
            category = Category.objects.get(name=request.query_params.get('category'))
            qs = self.get_queryset().filter(category=category)
            page = self.paginate_queryset(qs)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)

                categories = Category.objects.all()
                serializer = CategorySerializer(categories, many=True)
                response.data['categories'] = serializer.data
                return response

        else:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            response = super(ProductViewSet, self).list(request, *args, **kwargs)
            response.data['categories'] = serializer.data
            return response


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
