import random

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from inventory.models import Category, Product


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

        cls.product_size = 5
        cls.category_size = 3

        category_list = []
        for i in range(0, cls.category_size):
            category = Category.objects.create(
                name='category {}'.format(i)
            )
            category_list.append(category)

        for i in range(0, cls.product_size):
            random_cate_num = random.randint(0, cls.category_size - 1)
            Product.objects.create(
                name='product {}'.format(i),
                price=1000 * i,
                category=category_list[random_cate_num]
            )

    def login(self, user):
        refresh_token = RefreshToken.for_user(user)
        access_token = refresh_token.access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def logout(self):
        self.client.credentials()
