import rest_framework.exceptions
from django.db import transaction, DatabaseError
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied, ValidationError, MethodNotAllowed

from accounts.models import ShoppingCartItem
from ecommerce.pagination import DefaultPagination
from ecommerce.permissions import IsOwner
from inventory.models import ProductOption
from payment.models import Order, OrderItem, Payment
from payment.serializers import OrderDetailSerializer, OrderListSerializer, PaymentSerializer


class OrderViewSet(ModelViewSet):
    """
    주문 뷰셋: 주문 생성, 전체조회, 상세조회
    """
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.action in ['list']:
            serializer_class = OrderListSerializer
        elif self.action in ['retrieve', 'cancel', 'create', 'proceed_payment']:
            serializer_class = OrderDetailSerializer
        else:
            serializer_class = OrderListSerializer

        return serializer_class

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'cancel', 'proceed_payment']:
            permission_classes = [IsOwner, IsAuthenticated]
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated]
        else:
            raise MethodNotAllowed(self.action)

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-ordered_at')

    def create(self, request, *args, **kwargs):
        """
        주문 생성.
        Order와 OrderItem을 생성한다.

        @params
        [{ option(int): 옵션 아이디, qty(int): 수량 }]
        """
        result = {}
        try:
            with transaction.atomic():
                # 주문을 생성하고
                # 요청 데이터로 주문 아이템을 만든다.
                order = Order.objects.create(
                    user=self.request.user,
                )
                for order_item_data in request.data:
                    order_item = OrderItem.objects.create(
                        order=order,
                        option_id=order_item_data['option'],
                        qty=order_item_data['qty'],
                    )
                    order_item.amount = order_item.option.price * order_item_data['qty']
                    order_item.save()

                order.total_amount = order.get_total_amount()
                order.save_without_historical_record()

        except ValidationError as e:
            return Response({'error': e.detail}, status=400)
        except DatabaseError as e:
            return Response({'error': '오류가 발생했습니다.'}, status=500)

        return Response(OrderDetailSerializer(order).data, status=201)

    @action(detail=True, methods=['put'])
    def cancel(self, request, *args, **kwargs):
        order = self.get_object()
        order.cancel()
        order.refresh_from_db()
        return Response(OrderDetailSerializer(order).data, status=200)

    @action(detail=True, methods=['post'])
    def proceed_payment(self, request, *args, **kwargs):
        """
        주문 -> 주문 전체 금액 구하기 -> 결제 정보 생성 -> 결제 요청
        결제 성공: 결제 및 주문 상태 변경,
        결제 실패: 결제 주문 상태 변경

        @params
        payment_method(str)
        """
        order = self.get_object()
        is_mock_fail = False  # 결제 실패 테스트용

        if 'mock_fail' in request.data:
            is_mock_fail = request.data['mock_fail']

        if 'payment_method' not in request.data:
            return Response({'error': '결제정보를 찾을 수 없습니다.'}, status=400)

        if not request.data['payment_method'] in Payment.PAYMENT_METHOD.values:
            return Response({'error': '유효한 결제 방법이 아닙니다.'}, status=400)

        payment = Payment.objects.create(
            order=order,
            amount=order.get_total_amount(),
            payment_method=request.data['payment_method']
        )

        succeed, exception = payment.proceed_payment(mock_fail=is_mock_fail)

        if not succeed:
            return Response({'error': exception.detail['error_msg'], 'detail': {'order': order.id}}, status=500)

        ShoppingCartItem.objects.filter(cart=self.request.user.shoppingcart).delete()
        return Response(PaymentSerializer(payment).data, status=201)
