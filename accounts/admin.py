from django.contrib import admin
from accounts.models import User, ShoppingCartItem, ShoppingCart

admin.site.register(User)
admin.site.register(ShoppingCart)
admin.site.register(ShoppingCartItem)