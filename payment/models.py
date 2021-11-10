from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum
from simple_history.models import HistoricalRecords

from ecommerce.common import DEFAULT_SHIPPING_FEE
from payment.utils import PaymentService, PaymentError

User = get_user_model()


class Order(models.Model):
    class STATUS(models.IntegerChoices):
        CREATED = 0
        PAID = 1
        PAYMENT_FAILED = 2
        SHIPPING_READY = 3
        SHIPPING_COMPLETED = 4
        CANCELED = 5

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    status = models.SmallIntegerField(choices=STATUS.choices, default=STATUS.CREATED)
    total_amount = models.IntegerField(default=0)
    shipping_fee = models.IntegerField(default=DEFAULT_SHIPPING_FEE)
    ordered_at = models.DateTimeField(auto_now_add=True)
    order_log = HistoricalRecords()

    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True
        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret

    def cancel(self):
        self.status = self.STATUS.CANCELED
        self.save()

    def get_products_amount(self):
        return self.items.aggregate(amount=Sum('amount'))['amount']

    def get_total_amount(self):
        return self.get_products_amount() + self.shipping_fee


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    option = models.ForeignKey('inventory.ProductOption', on_delete=models.DO_NOTHING)
    qty = models.PositiveSmallIntegerField(default=0)
    amount = models.IntegerField('항목별 주문 금액', default=0)


class Payment(models.Model):
    class STATUS(models.IntegerChoices):
        CREATED = 0
        PAID = 1
        PAYMENT_FAILED = 2

    class PAYMENT_METHOD(models.TextChoices):
        TRANSFER = 'transfer'
        KAKAOPAY = 'kakaopay'
        NAVERPAY = 'naverpay'

    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, related_name='payments')
    amount = models.IntegerField('결제금액')
    status = models.SmallIntegerField(choices=STATUS.choices, default=STATUS.CREATED)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD.choices)
    paid_at = models.DateTimeField(auto_now_add=True)
    error_message = models.CharField(max_length=140)
    transfer_amount = models.IntegerField('무통장입금 금액', blank=True, null=True)
    transfer_name = models.IntegerField('무통장입금 입금자명', blank=True, null=True)
    transfer_bank = models.IntegerField('무통장입금 은행', blank=True, null=True)
    payment_log = HistoricalRecords()

    def proceed_payment(self, mock_fail=False):
        try:
            PaymentService.proceed_payment(
                email=self.order.user.email,
                amount=self.amount,
                payment_method=self.payment_method,
                mock_fail=mock_fail
            )

            self.order.status = self.order.STATUS.PAID
            self.order.save()

            self.status = self.STATUS.PAID
            self.save()
            return True, None

        except PaymentError as e:
            self.order.status = self.order.STATUS.PAYMENT_FAILED
            self.order.save()

            self.status = self.STATUS.PAYMENT_FAILED
            self.error_message = e.detail['error_msg']
            self.save()
            return False, e

