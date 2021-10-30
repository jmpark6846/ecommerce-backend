from django.contrib.auth import get_user_model
from ecommerce.tests import EcommerceTestCase
from inventory.models import Product, Category


class InventoryTestCase(EcommerceTestCase):
    def test_사용자는_로그인하지_않아도_상품을_조회할수있다(self):
        res = self.client.get('/products/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), self.product_size)

    def test_로그인한_사용자는_상품의_리뷰를_조회_생성_할수있다(self):
        self.login(self.user)
        product = Product.objects.last()
        res = self.client.get('/products/{}/reviews/'.format(product.id))
        self.assertEqual(res.status_code, 200)

        review_data = {
            'content': 'content1',
            'product': product.id,
            'author': self.user.pk
        }
        res = self.client.post('/products/{}/reviews/'.format(product.id), review_data)
        self.assertEqual(res.status_code, 201)