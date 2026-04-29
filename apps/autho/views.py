from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    AuthResponseSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    ResetPasswordConfirmSerializer,
    UserSerializer,
)

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: AuthResponseSerializer})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {"user": UserSerializer(user).data, "refresh": str(refresh), "access": str(refresh.access_token)},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LoginSerializer, responses={200: AuthResponseSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {"user": UserSerializer(user).data, "refresh": str(refresh), "access": str(refresh.access_token)}
        )


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=ForgotPasswordSerializer,
        responses={200: OpenApiResponse(description="If email exists, reset link was sent.")},
    )
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            # Don't leak whether a user exists.
            return Response({"detail": "If the email exists, a reset link was sent."})

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        frontend_url = request.data.get("frontend_url") 
        if frontend_url:
            reset_link = f"{frontend_url}?uid={uid}&token={token}"
        else:
            reset_link = f"/api/auth/password/reset/confirm/?uid={uid}&token={token}"

        send_mail(
            subject="Password reset",
            message=f"Use this link to reset your password: {reset_link}",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"detail": "If the email exists, a reset link was sent."})


class LogoutView(APIView):
    @extend_schema(request=LogoutSerializer, responses={200: OpenApiResponse(description="Logged out")})
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data["refresh"]
        token = RefreshToken(refresh)
        token.blacklist()
        return Response({"detail": "Logged out"})


class ResetPasswordConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=ResetPasswordConfirmSerializer,
        responses={200: OpenApiResponse(description="Password updated")},
    )
    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = serializer.get_user()
        except User.DoesNotExist:
            return Response({"detail": "Invalid uid"}, status=status.HTTP_400_BAD_REQUEST)

        if not token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response({"detail": "Password updated"})

class MeView(APIView):
    @extend_schema(
        summary="Get current logged in user profile",
        operation_id="my_profile",
        responses={200: UserSerializer}
    )
    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data)

class ProfileView(APIView):
    @extend_schema(
        summary="Get user profile by ID",
        operation_id="user_profile_by_id",
        responses={200: UserSerializer}
    )
    def get(self, request, user_id: int):
        if request.user.id != user_id and not getattr(request.user, "is_staff", False):
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)