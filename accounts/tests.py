import json

from accounts.models import ShoppingCartItem, ShoppingCart
from ecommerce.tests import EcommerceTestCase
from inventory.models import Product, ProductOption


class AccountTestCase(EcommerceTestCase):
    def test_사용자는_카트에_제품을_2개_추가하고_1개_삭제_할수있다(self):
        self.login(self.user)
        data = [{
                    'cart': self.user.shoppingcart.id,
                    'option': ProductOption.objects.last().id,
                    'qty': 1
                },{
                    'cart': self.user.shoppingcart.id,
                    'option': ProductOption.objects.first().id,
                    'qty': 2
                }]

        data = json.dumps(data)

        res = self.client.post('/accounts/{}/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        cart_item = ShoppingCartItem.objects.last()
        data = [cart_item.id]
        data = json.dumps(data)
        res = self.client.put('/accounts/{}/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 204)
        self.assertEqual(ShoppingCartItem.objects.count(), 1)

    def test_장바구니에_이미있는_옵션을_추가하면_기존의_옵션수량을_증가시킨다(self):
        self.login(self.user)
        cart_item = {
            'cart': self.user.shoppingcart.id,
            'option': ProductOption.objects.last().id,
            'qty': 1
        }
        data =  [cart_item]
        data = json.dumps(data)
        res = self.client.post('/accounts/{}/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        res = self.client.post('/accounts/{}/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(ShoppingCartItem.objects.count(), 1)
        cart_item = ShoppingCartItem.objects.filter(cart=self.user.shoppingcart).last()
        self.assertEqual(cart_item.qty, 2)

    def test_장바구니_항목_수량_변경(self):
        self.login(self.user)
        cart_item = {
            'cart': self.user.shoppingcart.id,
            'option': ProductOption.objects.last().id,
            'qty': 1
        }
        data = [cart_item]
        data = json.dumps(data)
        res = self.client.post('/accounts/{}/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        changed_qty = 3
        data = {
            'id': res.data[0]['id'],
            'qty': changed_qty
        }
        res = self.client.patch('/accounts/{}/cart/'.format(self.user.id), data)
        cart_item = ShoppingCartItem.objects.get(id=res.data['id'])
        self.assertEqual(cart_item.qty, changed_qty)