from django.urls import path, include
from rest_framework_nested import routers

from inventory.views import ProductViewSet, ProductReviewViewSet, CheckoutView, CartView

router = routers.SimpleRouter()
router.register('products', ProductViewSet, basename='products')

product_router = routers.NestedSimpleRouter(router, r'products', lookup='product')
product_router.register(r'reviews', ProductReviewViewSet, basename='product-reviews')

urlpatterns = [
    path('cart/checkout/', CheckoutView.as_view()),
    path('cart/', CartView.as_view()),
    path('', include(router.urls)),
    path('', include(product_router.urls))
]
