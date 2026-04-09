from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import ForgotPasswordView, LoginView, LogoutView, MeView, ProfileView, RegisterView, ResetPasswordConfirmView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", MeView.as_view(), name="auth-profile"),
    path("profile/<int:user_id>/", ProfileView.as_view(), name="auth-profile-by-id"),
    path("password/forgot/", ForgotPasswordView.as_view(), name="password-forgot"),
    path("password/reset/confirm/", ResetPasswordConfirmView.as_view(), name="password-reset-confirm"),
]
