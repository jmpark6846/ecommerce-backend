from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from ecommerce.models import BaseModel

User = get_user_model()


class Product(models.Model):
    name = models.CharField('상품 이름', max_length=120)
    price = models.IntegerField('가격')
    category = models.ForeignKey('inventory.Category', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('카테고리', max_length=120)

    def __str__(self):
        return self.name


class ProductReview(BaseModel):
    content = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content[:50]

