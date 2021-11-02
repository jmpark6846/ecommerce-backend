import random
import json
from django.db.models import Value

from ecommerce.tests import EcommerceTestCase
from inventory.models import ProductOption, Product
from payment.models import Order, OrderItem, Payment
from payment.serializers import get_change_from_histories


class PaymentTestCase(EcommerceTestCase):
    def setup_order_data(self):
        self.login(self.user)
        product = Product.objects.last()
        data = []
        option_qs = ProductOption.objects.filter(product=product)
        for option in option_qs:
            data.append({
                'option': option.id,
                'qty': random.randint(1, 5)
            })
        data = json.dumps(data)
        res = self.client.post('/orders/', data, content_type='application/json')
        order = Order.objects.get(id=res.data['id'])
        self.order = order

    def test_주문_전체_조회(self):
        self.setup_order_data()
        self.login(self.user)
        res = self.client.get('/orders/')
        self.assertEqual(res.status_code, 200)
        self.assertNotIn('order_log', res.data[0])

    def test_주문_상세_조회(self):
        self.setup_order_data()
        self.login(self.user)
        res = self.client.get('/orders/{}/'.format(self.order.id))
        self.assertEqual(res.status_code, 200)
        self.assertIn('order_log', res.data)

    def test_주문_생성(self):
        self.login(self.user)
        product = Product.objects.last()
        data = []
        option_qs = ProductOption.objects.filter(product=product)
        for option in option_qs:
            data.append({
                'option': option.id,
                'qty': random.randint(1, 5)
            })
        data = json.dumps(data)
        res = self.client.post('/orders/', data, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(len(res.data['items']), option_qs.count())

        # 로그 생성 확인
        order = Order.objects.last()
        self.assertEqual(order.order_log.count(), 1)

    def test_주문_취소(self):
        self.login(self.user)
        product = Product.objects.last()
        data = []
        option_qs = ProductOption.objects.filter(product=product)

        for option in option_qs:
            data.append({
                'option': option.id,
                'qty': random.randint(1, 5)
            })
        data = json.dumps(data)
        res = self.client.post('/orders/', data, content_type='application/json')
        res = self.client.put('/orders/{}/cancel/'.format(res.data['id']))
        self.assertEqual(res.status_code, 200)
        order = Order.objects.get(id=res.data['id'])

        self.assertEqual(order.status, Order.STATUS.CANCELED)

    def test_결제(self):
        self.setup_order_data()
        self.login(self.user)
        data = {'order': self.order.id, 'payment_method': Payment.PAYMENT_METHOD.NAVERPAY}
        res = self.client.post('/orders/{}/proceed_payment/',data)

        self.assertEqual(res.status_code, 201)
        self.order.refresh_from_db()
        self.assertIsNotNone(self.order.payments)
