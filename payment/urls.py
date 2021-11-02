from django.urls import path, include
from rest_framework_nested import routers

from payment.views import OrderViewSet

order_router = routers.SimpleRouter()
order_router.register('orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(order_router.urls)),
]
