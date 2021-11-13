from django.urls import path, include

from accounts.views import LogoutView

urlpatterns = [
    path('', include('dj_rest_auth.urls')),
    path('registration/', include('dj_rest_auth.registration.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
]