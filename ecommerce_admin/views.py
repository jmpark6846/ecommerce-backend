from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils import timezone

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ecommerce_admin.serializers import TopSellingItemsSerializers
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
        end = start + timezone.timedelta(days=6)
        end.replace(hour=23, minute=59, second=59)

        labels = [start + timezone.timedelta(days=i) for i in range(7)]

        qs = self.get_queryset().filter(paid_at__gte=start) \
            .values('paid_at__week_day') \
            .annotate(total_amount=Sum('amount'), date=TruncDate('paid_at')) \
            .values('total_amount', 'date') \
            .order_by('date')

        return Response({'labels': labels, 'qs': qs}, status=200)

    @action(detail=False, methods=['get'])
    def top_selling_items(self, request, *args, **kwargs):
        today = timezone.now()
        start_of_this_month = today.replace(day=1, hour=0, minute=0, second=0)
        order_paid_this_month_ids = Payment.objects.filter(
            paid_at__gt=start_of_this_month,
            order__status=Order.STATUS.PAID) \
            .values_list('order_id', flat=True)

        top_selling_items_qs = OrderItem.objects.filter(order_id__in=order_paid_this_month_ids) \
                                   .values('option') \
                                   .annotate(total_amount=Sum('amount'), total_qty=Sum('qty')) \
                                   .values('option', 'total_amount', 'total_qty') \
                                   .order_by('-total_amount')[:5]
        serializer = TopSellingItemsSerializers(top_selling_items_qs, many=True, context={'request': request})
        return Response(serializer.data, status=200)
