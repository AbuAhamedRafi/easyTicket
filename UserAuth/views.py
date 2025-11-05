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
    LoginSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    ResendVerificationSerializer,
    LogoutSerializer,
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
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Registration successful. Please check your email to verify your account.",
                "user": {
                    "id": str(user.id),
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
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Email verified successfully. You can now login.",
                "user": {
                    "id": str(user.id),
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

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthThrottle]  # Rate limit: 5 requests per hour

    @extend_schema(
        summary="User login",
        description="Authenticate user and return JWT tokens. Email must be verified.",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Update last login
        user.save(update_fields=["last_login"])

        return Response(
            {
                "message": "Login successful",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


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
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
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

    serializer_class = UserSerializer
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

    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Change password",
        description="Change the authenticated user's password",
        tags=["Authentication"],
    )
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
    Body: {"refresh": "refresh-token"}
    Returns new access token
    """

    @extend_schema(
        summary="Refresh JWT token",
        description="Get a new access token using the refresh token",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
