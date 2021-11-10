from django.urls import path, include
from rest_framework_nested import routers

from ecommerce_admin.views import PaymentAdminViewSet

admin_payment_router = routers.SimpleRouter()
admin_payment_router.register('payments', PaymentAdminViewSet, basename='admin-payment')

urlpatterns = [
    path('', include(admin_payment_router.urls)),
]
