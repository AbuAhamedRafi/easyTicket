from django.urls import path
from .views import (
    UserRegistrationView,
    EmailVerificationView,
    LoginView,
    LogoutView,
    CurrentUserView,
    ChangePasswordView,
    ResendVerificationView,
    CustomTokenRefreshView,
)

app_name = "userauth"

urlpatterns = [
    # Authentication endpoints
    path("signup/", UserRegistrationView.as_view(), name="signup"),
    path("verify-email/", EmailVerificationView.as_view(), name="verify-email"),
    path(
        "resend-verification/",
        ResendVerificationView.as_view(),
        name="resend-verification",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    # JWT Token endpoints
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token-refresh"),
    # User profile endpoints
    path("profile/", CurrentUserView.as_view(), name="current-user"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
