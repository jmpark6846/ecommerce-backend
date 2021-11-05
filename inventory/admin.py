from django.contrib import admin

from inventory.models import Product, ProductReview, Category, ProductImage, ProductOption


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'file', 'uploaded_at')


class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'value', 'product_price', 'price', 'is_default')

    @admin.display(
        description='상품가'
    )
    def product_price(self, obj):
        return obj.product.price


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(ProductOption, ProductOptionAdmin)
admin.site.register(ProductReview)
admin.site.register(Category)
