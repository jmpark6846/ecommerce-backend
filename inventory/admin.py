from django.contrib import admin

from inventory.models import Product, ProductReview, Category


admin.site.register(Product)
admin.site.register(ProductReview)
admin.site.register(Category)

