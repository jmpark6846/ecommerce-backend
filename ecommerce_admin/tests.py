from django.utils import timezone
from rest_framework.utils import json

from ecommerce.tests import EcommerceTestCase
from inventory.models import ProductOption
from payment.models import Payment


class AdminDashboardTestCase(EcommerceTestCase):
    def do_order(self, **kwargs):
        option_id = kwargs.get('option_id', ProductOption.objects.last().id)
        ordered_at = kwargs.get('ordered_at', timezone.now())

        self.login(self.user)

        # 장바구니 추가
        cart_item = {
            'cart': self.user.shoppingcart.id,
            'option': option_id,
            'qty': 1
        }
        data = [cart_item]
        data = json.dumps(data)
        res = self.client.post('/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # 체크아웃
        res = self.client.post('/cart/checkout/'.format(self.user.id))
        self.assertEqual(res.status_code, 201)
        order_id = res.data['order']['id']

        # 결제
        data = {'order': order_id, 'payment_method': Payment.PAYMENT_METHOD.NAVERPAY}
        res = self.client.post('/orders/{}/proceed_payment/'.format(order_id), data)
        self.assertEqual(res.status_code, 201)

        paid_at = ordered_at
        payment = Payment.objects.get(id=res.data['id'])
        payment.paid_at = paid_at
        payment.save()
        return payment.order, payment

    def test_일별_매출조회(self):
        ten_days_ago = timezone.now() - timezone.timedelta(days=10)
        self.do_order()
        self.do_order()
        order, payment = self.do_order()
        self.do_order(ordered_at=ten_days_ago)
        weekday_of_today = timezone.now().weekday() + 2
        self.login(self.superuser)
        res = self.client.get('/ecommerce_admin/payments/weeks/')
        self.assertEqual(res.status_code, 200)
        # data = list(filter(lambda x: x['week_day'] == weekday_of_today, res.data))[0]
        # self.assertEqual(data['total_amount'], payment.amount * 3)

    def test_이번달_매출_상위제품(self):
        # 옵션 3개를 각각 따로 주문, 마지막 옵션은 하나 더 주문
        qs = ProductOption.objects.all()[:3]
        for option in qs:
            self.do_order(option_id=option.id)

        option = qs[2]
        self.do_order(option_id=option.id)

        self.login(self.superuser)
        res = self.client.get('/ecommerce_admin/payments/top_selling_items/')
        self.assertEqual(res.status_code, 200)

        # 2개 주문한 옵션의 매출은 옵션 가격의 2배
        option_data = list(filter(lambda x: x['option']['id'] == option.id, res.data))[0]
        self.assertEqual(option_data['total_amount'], option.price * 2)
