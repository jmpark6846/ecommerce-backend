from django.utils import timezone
from rest_framework.utils import json

from accounts.models import ShoppingCartItem
from ecommerce.tests import EcommerceTestCase
from inventory.models import ProductOption, Category
from payment.models import Payment, Order, OrderItem
import random


class AdminTestCase(EcommerceTestCase):
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
        data = list(filter(lambda x: x['week_day'] == weekday_of_today, res.data))[0]
        self.assertEqual(data['total_amount'], payment.amount * 3)

    def test_카테고리별_최고_매출_상품과_금액(self):
        # category
        cat_qs = Category.objects.all()
        for category in cat_qs:
            option = ProductOption.objects.filter(product__category=category).last()
            self.do_order(option_id=option.id)

        # 마지막 카테고리의 상품하나 더 주문, 총 2개 구매
        last_category = Category.objects.last()
        option = ProductOption.objects.filter(product__category=last_category).last()
        order, payment = self.do_order(option_id=option.id)

        '''
        [(category, ProductOption, amount), ...]
        '''


        self.login(self.superuser)
        res = self.client.get('/ecommerce_admin/payments/this_month_by_category/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), Category.objects.count())

        last_cate_data = list(filter(lambda x: x['category'] == last_category.id, res.data))[0]
        self.assertEqual(last_cate_data['total_amount'], option.price * 2)
