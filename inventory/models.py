from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save

from ecommerce.common import DEFAULT_SHIPPING_FEE
from ecommerce.models import BaseModel

User = get_user_model()


class Product(models.Model):
    name = models.CharField('상품 이름', max_length=120)
    price = models.IntegerField('가격')
    category = models.ForeignKey('inventory.Category', on_delete=models.DO_NOTHING)
    shipping_fee = models.IntegerField(default=DEFAULT_SHIPPING_FEE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.productimage_set:
            ProductOption.objects.create(
                product=self,
                name='기본',
                value='기본',
                price=self.price,
                is_default=True
            )
        super(Product, self).save(*args, **kwargs)


def product_image_directory_path(instance, filename):
    return 'product_image/{0}/{1}'.format(instance.product.name, filename)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.ImageField(upload_to=product_image_directory_path, blank=True, null=True)
    name = models.CharField('이미지 이름', max_length=80)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ProductOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField('옵션명', max_length=80)
    value = models.CharField('옶션값', max_length=120)
    price = models.IntegerField('옵션 가격')
    is_default = models.BooleanField('기본 여부', default=False)

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
