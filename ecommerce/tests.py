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

        user2 = User.objects.create(
            email='test2@test.co',
            username='test2',
            is_staff=True,
        )
        user2.set_password('test2')
        cls.superuser = user2

        cls.client = APIClient()

        cls.productoption_size = 3
        cls.category_size = 3

        category_list = []
        for i in range(0, cls.category_size):
            category = Category.objects.create(
                name='category {}'.format(i)
            )
            category_list.append(category)

        for category in category_list:
            product = Product.objects.create(
                name='product {}'.format(i),
                price=1000,
                category=category
            )
            for j in range(0, cls.productoption_size):
                ProductOption.objects.create(
                    product=product,
                    name='product option {}'.format(j),
                    value='product option value {}'.format(j),
                    price=1000*j
                )

    def login(self, user):
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def logout(self):
        self.client.credentials()
