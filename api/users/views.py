from django.contrib.sites.shortcuts import get_current_site
from rest_framework import generics, mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import CustomUser
from users.permissions import UserAccessOrReadOnly
from users.serializers import (
    UserListSerializer, UserCreateSerializer, UserDetailSerializer,
    EmailConfirmSerializer, ChangePasswordSerializer, EmailSerializer,
    PasswordResetSerializer
)
from users.utils import send_password_reset_email


class UserListViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [UserAccessOrReadOnly]


class EmailConfirmView(generics.GenericAPIView):
    serializer_class = EmailConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(id=serializer.validated_data['id'])
        user.is_active = True
        user.save()
        return Response(
            {'message': 'Email confirmed with success.'},
            status=status.HTTP_200_OK
        )


class ChangePasswordView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        super(ChangePasswordView, self).update(request, *args, **kwargs)
        return Response(
            {'message': 'Password updated successfully.'},
            status=status.HTTP_200_OK
        )


class PasswordReset(generics.GenericAPIView):
    serializer_class = EmailSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        user = CustomUser.objects.get(email=email)
        domain = get_current_site(request)
        send_password_reset_email(user, domain)
        return Response(
            {'message': 'We have sent you a link to reset your password.'},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirm(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(id=serializer.validated_data['id'])
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response(
            {'message': 'Password changed successfully.'},
            status=status.HTTP_200_OK
        )
