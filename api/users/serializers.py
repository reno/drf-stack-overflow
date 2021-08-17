from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from users.models import CustomUser
from users.tokens import email_confirmation_token
from users.utils import send_confirmation_email


class UserListSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users:detail')

    class Meta:
        model = CustomUser
        fields = ['url', 'username', 'location', 'picture']


class UserDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users:detail')

    class Meta:
        model = CustomUser
        fields = [
            'url',
            'username',
            'first_name',
            'last_name',
            'email',
            'picture',
            'location',
            'job_title',
            'bio',
            'website_url',
            'twitter_account',
            'github_account'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password],
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'first_name',
            'last_name',
            'username',
            'password',
            'password2',
            'picture',
            'location',
            'job_title',
            'bio',
            'website_url',
            'twitter_account',
            'github_account'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'detail': "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = super(UserCreateSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        domain = get_current_site(self.context['request'])
        send_confirmation_email(user, domain)
        return user


class EmailConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(write_only=True, required=True)
    token = serializers.CharField(write_only=True, required=True)
    id = serializers.HiddenField(default=None)

    def validate(self, attrs):
        try:
            attrs['id'] = force_text(urlsafe_base64_decode(attrs['uidb64']))
            user = CustomUser.objects.get(id=attrs['id'])
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            raise ParseError('Invalid uid.')
        if not email_confirmation_token.check_token(user, attrs['token']):
            raise ParseError('Invalid token.')
        return attrs


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password],
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['old_password', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'detail': "Password fields didn't match."}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Wrong password.')
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email not registered.')
        return value


class PasswordResetSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(write_only=True, required=True)
    token = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password],
    )
    password2 = serializers.CharField(write_only=True, required=True)
    id = serializers.HiddenField(default=None)

    def validate(self, attrs):
        try:
            attrs['id'] = force_text(urlsafe_base64_decode(attrs['uidb64']))
            user = CustomUser.objects.get(id=attrs['id'])
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            raise ParseError('Invalid uid.')
        if not PasswordResetTokenGenerator().check_token(user, attrs['token']):
            raise ParseError('Invalid token.')
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'detail': "Password fields didn't match."}
            )
        return attrs


