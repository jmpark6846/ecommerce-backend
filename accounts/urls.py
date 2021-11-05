from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns

from accounts.views import CartView, CheckoutView

urlpatterns = [
    path('<int:pk>/cart/checkout/', CheckoutView.as_view()),
    path('<int:pk>/cart/', CartView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

