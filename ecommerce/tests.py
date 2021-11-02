import random

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from inventory.models import Category, Product, ProductOption


class EcommerceTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        user = User.objects.create(
            email='test@test.co',
            username='test'
        )
        user.set_password('test')
        cls.user = user
        cls.client = APIClient()

        cls.product_size = 3
        cls.category_size = 3

        category_list = []
        for i in range(0, cls.category_size):
            category = Category.objects.create(
                name='category {}'.format(i)
            )
            category_list.append(category)

        for i in range(0, cls.product_size):
            random_cate_num = random.randint(0, cls.category_size - 1)
            product = Product.objects.create(
                name='product {}'.format(i),
                price=1000 * i,
                category=category_list[random_cate_num]
            )

            for j in range(0, 3):
                ProductOption.objects.create(
                    product=product,
                    name='product option {}'.format(j),
                    value='product option value {}'.format(j),
                    price=product.price+100*j
                )

    def login(self, user):
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def logout(self):
        self.client.credentials()
