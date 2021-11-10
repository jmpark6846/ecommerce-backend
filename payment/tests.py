import random
import json
from django.db.models import Value

from accounts.models import ShoppingCartItem
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
        self.assertNotIn('order_log', res.data['list'][0])

    def test_주문_상세_조회(self):
        self.setup_order_data()
        self.login(self.user)
        res = self.client.get('/orders/{}/'.format(self.order.id))
        self.assertEqual(res.status_code, 200)
        self.assertIn('order_log', res.data)

    def test_체크아웃(self):
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
        res = self.client.post('/orders/{}/proceed_payment/'.format(self.order.id), data)

        self.assertEqual(res.status_code, 201)
        self.order.refresh_from_db()
        self.assertIsNotNone(self.order.payments)

    def test_장바구니_추가_주문_결제(self):
        self.login(self.user)

        # 장바구니 추가
        cart_item = {
            'cart': self.user.shoppingcart.id,
            'option': ProductOption.objects.last().id,
            'qty': 1
        }
        data = [cart_item]
        data = json.dumps(data)
        res = self.client.post('/accounts/{}/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        # 체크아웃
        res = self.client.post('/accounts/{}/cart/checkout/'.format(self.user.id))
        self.assertEqual(res.status_code, 201)
        order_id = res.data['order']['id']

        # 결제
        data = {'order': order_id, 'payment_method': Payment.PAYMENT_METHOD.NAVERPAY}
        res = self.client.post('/orders/{}/proceed_payment/'.format(order_id), data)
        self.assertEqual(res.status_code, 201)

        # 결제 후 장바구니를 비운다.
        cart_item_count = ShoppingCartItem.objects.filter(cart=self.user.shoppingcart).count()
        self.assertEqual(cart_item_count, 0)

    def test_결제실패_재시도(self):
        self.setup_order_data()
        self.login(self.user)
        self.assertEqual(self.order.order_log.count(), 1)

        data = {'mock_fail': True, 'order': self.order.id, 'payment_method': Payment.PAYMENT_METHOD.NAVERPAY}
        res = self.client.post('/orders/{}/proceed_payment/'.format(self.order.id), data)
        self.assertEqual(res.status_code, 500)
        self.assertEqual(self.order.order_log.count(), 2)

        del data['mock_fail']
        res = self.client.post('/orders/{}/proceed_payment/'.format(self.order.id), data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(self.order.order_log.count(), 3)

        self.order.refresh_from_db()

    def test_주문취소(self):
        pass
