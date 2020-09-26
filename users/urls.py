from django.urls import path, include
from . import views

urlpatterns = [
    path("reset-password/", views.UserPasswordResetView.as_view(), name="rest_password_reset"),
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
]
