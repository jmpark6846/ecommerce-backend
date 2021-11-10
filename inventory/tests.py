from rest_framework import status

from ecommerce.tests import EcommerceTestCase
from inventory.models import Product, ProductReview, Category, ProductOption


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

