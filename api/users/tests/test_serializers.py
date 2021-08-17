import json
import os
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.exceptions import ParseError
from rest_framework.serializers import ValidationError
from rest_framework.test import APITestCase, APIRequestFactory
from users.serializers import (
    UserCreateSerializer, EmailConfirmSerializer, ChangePasswordSerializer,
    EmailSerializer, PasswordResetSerializer
)
from users.tokens import email_confirmation_token

User = get_user_model()


class UserCreateSerializerTestCase(TestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'data.json')
        with open(file_path) as file:
            data = json.load(file)
        self.user_data = data.get('user_data')
        self.user_data['password2'] = self.user_data['password']

    def test_validate(self):
        serializer = UserCreateSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())

    def test_validate_wrong_data(self):
        with self.assertRaisesMessage(
                ValidationError, "Password fields didn't match."
        ):
            self.user_data['password2'] = 's0m3p4assw0rd'
            serializer = UserCreateSerializer(data=self.user_data)
            serializer.is_valid(raise_exception=True)

    def test_create(self):
        url = reverse('users:list')
        factory = APIRequestFactory()
        request = factory.get(url)
        serializer = UserCreateSerializer(
            data=self.user_data, context = {'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, 'Django app account verification'
        )


class EmailConfirmSerializerTestCase(TestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'data.json')
        with open(file_path) as file:
            data = json.load(file)
        user_data = data.get('user_data')
        self.user = User.objects.create_user(**user_data)

    def test_validate(self):
        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(self.user.id)),
            'token': email_confirmation_token.make_token(self.user),
        }
        serializer = EmailConfirmSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_wrong_id(self):
        with self.assertRaisesMessage(ParseError, 'Invalid uid.'):
            data = {
                'uidb64': urlsafe_base64_encode(force_bytes(9999)),
                'token': email_confirmation_token.make_token(self.user),
            }
            serializer = EmailConfirmSerializer(data=data)
            serializer.is_valid(raise_exception=True)

    def test_validate_wrong_token(self):
        with self.assertRaisesMessage(ParseError, 'Invalid token.'):
            data = {
                'uidb64': urlsafe_base64_encode(force_bytes(self.user.id)),
                'token': 'invalid-token',
            }
            serializer = EmailConfirmSerializer(data=data)
            serializer.is_valid(raise_exception=True)


class ChangePasswordSerializerTestCase(APITestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'data.json')
        with open(file_path) as file:
            data = json.load(file)
        self.user_data = data.get('user_data')
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        factory = APIRequestFactory()
        url = reverse('users:change-password', args=[user.id])
        self.request = factory.get(url)
        self.request.user = user

    def test_validate(self):
        data = {
            'old_password': self.user_data['password'],
            'password': '4n0th3rp4ssw0rd',
            'password2': '4n0th3rp4ssw0rd'
        }
        serializer = ChangePasswordSerializer(
            data=data, context={'request': self.request}
        )
        self.assertTrue(serializer.is_valid())

    def test_validate_wrong_data(self):
        with self.assertRaisesMessage(
                ValidationError, "Password fields didn't match."
        ):
            data = {
                'old_password': self.user_data['password'],
                'password': '4n0th3rp4ssw0rd',
                'password2': 'unmached'
            }
            serializer = ChangePasswordSerializer(
                data=data, context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)

    def test_validate_wrong_password(self):
        with self.assertRaisesMessage(ValidationError, 'Wrong password.'):
            data = {
                'old_password': 'wrong-password',
                'password': '4n0th3rp4ssw0rd',
                'password2': '4n0th3rp4ssw0rd'
            }
            serializer = ChangePasswordSerializer(
                data=data, context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)


class EmailSerializerTestCase(TestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'data.json')
        with open(file_path) as file:
            data = json.load(file)
        self.user_data = data.get('user_data')
        User.objects.create_user(**self.user_data)

    def test_validate_email(self):
        data = {'email': self.user_data['email']}
        serializer = EmailSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_wrong_email(self):
        with self.assertRaisesMessage(ValidationError, 'Email not registered.'):
            data = {'email': 'wrong@mail.com'}
            serializer = EmailSerializer(data=data)
            serializer.is_valid(raise_exception=True)


class PasswordResetSerializerTestCase(TestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'data.json')
        with open(file_path) as file:
            data = json.load(file)
        self.user_data = data.get('user_data')
        self.user = User.objects.create_user(**self.user_data)

    def test_validate(self):
        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(self.user.id)),
            'token': PasswordResetTokenGenerator().make_token(self.user),
            'password': self.user_data['password'],
            'password2': self.user_data['password']
        }
        serializer = PasswordResetSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_wrong_password(self):
        with self.assertRaisesMessage(
                ValidationError, "Password fields didn't match."
        ):
            data = {
                'uidb64': urlsafe_base64_encode(force_bytes(self.user.id)),
                'token': PasswordResetTokenGenerator().make_token(self.user),
                'password': self.user_data['password'],
                'password2': 'unmatched'
            }
            serializer = PasswordResetSerializer(data=data)
            serializer.is_valid(raise_exception=True)

    def test_validate_wrong_id(self):
        with self.assertRaisesMessage(ParseError, 'Invalid uid.'):
            data = {
                'uidb64': urlsafe_base64_encode(force_bytes(9999)),
                'token': PasswordResetTokenGenerator().make_token(self.user),
                'password': self.user_data['password'],
                'password2': self.user_data['password']
            }
            serializer = PasswordResetSerializer(data=data)
            serializer.is_valid(raise_exception=True)

    def test_validate_wrong_token(self):
        with self.assertRaisesMessage(ParseError, 'Invalid token.'):
            data = {
                'uidb64': urlsafe_base64_encode(force_bytes(self.user.id)),
                'token': 'invalid-token',
                'password': self.user_data['password'],
                'password2': self.user_data['password']
            }
            serializer = PasswordResetSerializer(data=data)
            serializer.is_valid(raise_exception=True)

