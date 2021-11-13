import json
from rest_framework import status

from ecommerce.tests import EcommerceTestCase
from inventory.models import Product, ProductReview, Category, ProductOption, ShoppingCartItem


class InventoryTestCase(EcommerceTestCase):
    def test_사용자는_로그인하지_않아도_상품을_조회할수있다(self):
        res = self.client.get('/products/')
        self.assertEqual(res.status_code, 200)


    def test_로그인한_사용자는_상품의_리뷰를_생성_할수있다(self):
        self.login(self.user)
        product = Product.objects.last()
        review_data = {
            'content': 'content1',
            'product': product.id,
            'author': self.user.pk
        }
        res = self.client.post('/products/{}/reviews/'.format(product.id), review_data)
        self.assertEqual(res.status_code, 201)

    def test_로그인한_사용자는_자신의_상품리뷰를_수정_삭제_할수있다(self):
        self.login(self.user)
        product = Product.objects.last()
        review = ProductReview.objects.create(
            content="content",
            product=product,
            author=self.user
        )
        review_data = {
            'content': 'content_updated',
            'product': product.id,
            'author': self.user.pk
        }
        res = self.client.put('/products/{}/reviews/{}/'.format(product.id, review.id), review_data)
        self.assertEqual(res.status_code, 200)

        res = self.client.delete('/products/{}/reviews/{}/'.format(product.id, review.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class SearchTestCase(EcommerceTestCase):
    def test_검색(self):
        product = Product.objects.create(
            name='나이키',
            price=10000,
            category=Category.objects.last()
        )
        ProductOption.objects.create(
            product=product,
            name='색상',
            value='흰색',
            price=12000,
        )
        ProductOption.objects.create(
            product=product,
            name='색상',
            value='검은색',
            price=12000,
        )
        search_term = "나이키"
        res = self.client.get('/products/?search={}'.format(search_term))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['count'], 1)


class CartTestCase(EcommerceTestCase):
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

        res = self.client.post('/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        cart_item = ShoppingCartItem.objects.last()
        data = [cart_item.id]
        data = json.dumps(data)
        res = self.client.put('/cart/'.format(self.user.id), data, content_type='application/json')
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
        res = self.client.post('/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        res = self.client.post('/cart/'.format(self.user.id), data, content_type='application/json')
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
        res = self.client.post('/cart/'.format(self.user.id), data, content_type='application/json')
        self.assertEqual(res.status_code, 201)

        changed_qty = 3
        data = {
            'id': res.data[0]['id'],
            'qty': changed_qty
        }
        res = self.client.patch('/cart/'.format(self.user.id), data)
        cart_item = ShoppingCartItem.objects.get(id=res.data['id'])
        self.assertEqual(cart_item.qty, changed_qty)