import json

from accounts.models import ShoppingCartItem, ShoppingCart
from ecommerce.tests import EcommerceTestCase
from inventory.models import Product, ProductOption


class AccountTestCase(EcommerceTestCase):
    def test_사용자_수정(self):
        self.user.username = "chagned!"
        self.user.save()
        self.assertEqual(ShoppingCart.objects.count(), 1)


    def test_사용자는_카트에_제품을_추가_삭제_할수있다(self):
        self.login(self.user)
        cart_item_size = 3

        cart_item = {
            'cart': self.user.shoppingcart.id,
            'option': ProductOption.objects.last().id,
            'qty': 2
        }
        data = {
            'items': [cart_item] * cart_item_size
        }

        data = json.dumps(data)
        res = self.client.post('/accounts/{}/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        cart_item = ShoppingCartItem.objects.last()
        data = {
            'items': [cart_item.id]
        }
        data = json.dumps(data)
        res = self.client.delete('/accounts/{}/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 204)
        self.assertEqual(ShoppingCartItem.objects.count(), cart_item_size - 1)

