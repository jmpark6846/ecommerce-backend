from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save

from ecommerce.models import BaseModel

User = get_user_model()


class Product(models.Model):
    name = models.CharField('상품 이름', max_length=120)
    price = models.IntegerField('가격')
    category = models.ForeignKey('inventory.Category', on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField('옵션명', max_length=80)
    value = models.CharField('옶션값', max_length=120)
    price = models.IntegerField('옵션 가격')

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
