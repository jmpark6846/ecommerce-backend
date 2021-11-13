from django.contrib.postgres.search import SearchVector
from rest_framework import status
from rest_framework.mixins import RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from ecommerce.pagination import DefaultPagination, ProductPagination
from inventory.models import Product, ProductReview, Category, ShoppingCartItem
from ecommerce.permissions import IsAuthor, IsOwner
from inventory.serializers import ProductReviewSerializer, ProductListSerializer, \
    ProductDetailSerializer, CategorySerializer
from payment.models import Order, OrderItem
from payment.serializers import ShoppingCartItemSerializer, OrderDetailSerializer


class ProductViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Product.objects.order_by('created_at')
    pagination_class = ProductPagination

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


class CartView(APIView):
    permission_classes = [IsOwner, IsAuthenticated]

    def get(self, request, *args, **kwargs):
        qs = ShoppingCartItem.objects.filter(cart=self.request.user.shoppingcart)
        serializer = ShoppingCartItemSerializer(qs, context={'request': request}, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        serializer = ShoppingCartItemSerializer(data=request.data, context={'cart': request.user.shoppingcart},
                                                many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    def patch(self, request, *args, **kwargs):
        cart_item = ShoppingCartItem.objects.get(id=request.data['id'])
        cart_item.qty = request.data['qty']
        cart_item.save()
        return Response(ShoppingCartItemSerializer(cart_item).data, status=200)

    def put(self, request, *args, **kwargs):
        qs = ShoppingCartItem.objects.filter(id__in=request.data)
        qs.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckoutView(APIView):
    permission_classes = [IsOwner, IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart_items: [ShoppingCartItem] = self.request.user.shoppingcart.items.all()
        order = Order.objects.create(user=self.request.user)

        if cart_items.count() == 0:
            return Response({'error': '장바구니가 비어있습니다.'}, status=400)

        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                option=cart_item.option,
                qty=cart_item.qty,
            )
            order_item.amount = cart_item.option.price * cart_item.qty
            order_item.save()

        order.total_amount = order.get_total_amount()
        order.save()

        return Response({'order': OrderDetailSerializer(order).data}, status=201)

