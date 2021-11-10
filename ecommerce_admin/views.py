from django.db.models import Sum, F
from django.utils import timezone

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from payment.models import Payment, OrderItem, Order
from payment.serializers import PaymentSerializer


class PaymentAdminViewSet(ModelViewSet):
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=False, methods=['get'])
    def weeks(self, request, *args, **kwargs):
        today = timezone.now()
        # start = today - timezone.timedelta(days=14)
        start = today - timezone.timedelta(days=today.weekday())
        start.replace(hour=0, minute=0, second=0)
        # end = start + timezone.timedelta(days=6)
        # end.replace(hour=23, minute=59, second=59)
        # print(start, end)
        # payment = Payment.objects.filter(paid_at__week_day=)

        qs = self.get_queryset().filter(paid_at__gt=start) \
            .values('paid_at__week_day') \
            .annotate(total_amount=Sum('amount'), week_day=F('paid_at__week_day')) \
            .values('total_amount', 'week_day') \
            .order_by('week_day')
        return Response(qs, status=200)

    @action(detail=False, methods=['get'])
    def this_month_by_category(self, request, *args, **kwargs):
        '''
        [(category, ProductOption, amount), ...]
        '''
        today = timezone.now()
        # start = today - timezone.timedelta(days=14)
        start_of_this_month = today.replace(day=1, hour=0, minute=0, second=0)
        order_paid_this_month_ids = Payment.objects.filter(
            paid_at__gt=start_of_this_month,
            order__status=Order.STATUS.PAID) \
            .values_list('order_id', flat=True)

        qs = OrderItem.objects.filter(order_id__in=order_paid_this_month_ids)\
            .values('option__product__category') \
            .annotate(total_amount=Sum('amount'),
                      category=F('option__product__category'),
                      product=F('option__product'))\
            .values('category','product','total_amount')\
            .order_by('category')

        print(qs)
        return Response(qs, status=200)
