from django.db import transaction
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from Common.throttling import AuthThrottle
from .serializers import (
    UserRegistrationSerializer,
    EmailVerificationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    ResendVerificationSerializer,
    LogoutSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    GoogleSignInSerializer,
)
from .models import User


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    POST /api/auth/signup/
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]  # Rate limit: 5 requests per hour

    @extend_schema(
        summary="Register a new user",
        description="Create a new user account (consumer or organizer). Email verification required before login.",
        tags=["Authentication"],
    )
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Registration successful. Please check your email to verify your account.",
                "user": {
                    "uid": str(user.uid),
                    "email": user.email,
                    "user_type": user.user_type,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class EmailVerificationView(generics.GenericAPIView):
    """
    API endpoint for email verification
    POST /api/auth/verify-email/
    Body: {"token": "verification-token"}
    """

    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Verify email address",
        description="Verify user email using the token sent via email",
        tags=["Authentication"],
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Email verified successfully. You can now login.",
                "user": {
                    "uid": str(user.uid),
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )


class LoginView(generics.GenericAPIView):
    """
    API endpoint for user login
    POST /api/auth/login/
    Body: {"email": "user@example.com", "password": "password"}
    Returns JWT tokens
    """

    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]  # Rate limit: 5 requests per hour

    @extend_schema(
        summary="User login",
        description="Authenticate user and return JWT tokens. Email must be verified.",
        tags=["Authentication"],
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Update last login
        user.save(update_fields=["last_login"])

        # Prepare response
        response = Response(
            {
                "message": "Login successful",
                "tokens": {
                    "refresh": refresh_token,
                    "access": access_token,
                },
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

        # Set HTTP-only cookies for tokens
        from django.conf import settings

        # Access token cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
            httponly=True,
            secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
            samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
            path="/",
        )

        # Refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
            httponly=True,
            secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
            samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
            path="/",
        )

        return response


class LogoutView(generics.GenericAPIView):
    """
    API endpoint for user logout
    POST /api/auth/logout/
    Body: {"refresh": "refresh-token"}
    Blacklists the refresh token
    """

    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="User logout",
        description="Blacklist the refresh token to logout user",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        try:
            # Try to get refresh token from request body or cookies
            refresh_token = request.data.get("refresh") or request.COOKIES.get(
                "refresh_token"
            )

            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            # Prepare response
            response = Response(
                {"message": "Logout successful"}, status=status.HTTP_200_OK
            )

            # Clear cookies
            response.delete_cookie("access_token", path="/")
            response.delete_cookie("refresh_token", path="/")

            return response

        except Exception as e:
            return Response(
                {"error": "Invalid token or token already blacklisted"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    API endpoint to get/update current user profile
    GET /api/auth/profile/
    PUT/PATCH /api/auth/profile/
    """

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get or update current user profile",
        description="Retrieve or update the authenticated user's profile information",
        tags=["Authentication"],
    )
    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    """
    API endpoint to change password
    POST /api/auth/change-password/
    Body: {
        "old_password": "current",
        "new_password": "new",
        "new_password_confirm": "new"
    }
    """

    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change password",
        description="Change the authenticated user's password",
        tags=["Authentication"],
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password changed successfully"}, status=status.HTTP_200_OK
        )


class ResendVerificationView(generics.GenericAPIView):
    """
    API endpoint to resend verification email
    POST /api/auth/resend-verification/
    Body: {"email": "user@example.com"}
    """

    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Resend verification email",
        description="Resend email verification link to user",
        tags=["Authentication"],
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Verification email sent successfully"},
            status=status.HTTP_200_OK,
        )


class CustomTokenRefreshView(TokenRefreshView):
    """
    API endpoint to refresh JWT access token
    POST /api/auth/token/refresh/
    Body: {"refresh": "refresh-token"} or reads from cookie
    Returns new access token
    """

    @extend_schema(
        summary="Refresh JWT token",
        description="Get a new access token using the refresh token",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        # Try to get refresh token from request body or cookies
        refresh_token = request.data.get("refresh") or request.COOKIES.get(
            "refresh_token"
        )

        if refresh_token:
            request.data._mutable = True
            request.data["refresh"] = refresh_token
            request.data._mutable = False

        # Get the response from parent class
        response = super().post(request, *args, **kwargs)

        # If successful, set new access token in cookie
        if response.status_code == 200:
            access_token = response.data.get("access")

            if access_token:
                from django.conf import settings

                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    max_age=settings.SIMPLE_JWT[
                        "ACCESS_TOKEN_LIFETIME"
                    ].total_seconds(),
                    httponly=True,
                    secure=settings.SIMPLE_JWT.get("AUTH_COOKIE_SECURE", False),
                    samesite=settings.SIMPLE_JWT.get("AUTH_COOKIE_SAMESITE", "Lax"),
                    path="/",
                )

        return response
