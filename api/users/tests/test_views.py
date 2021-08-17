import json
import os
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from users.serializers import UserListSerializer, UserDetailSerializer
from users.tokens import email_confirmation_token

User = get_user_model()


class UserViewsTestCase(APITestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'data.json')
        with open(file_path) as file:
            data = json.load(file)
        self.user_data = data.get('user_data')
        self.another_user_data = data.get('another_user_data')
        self.user = User.objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()
        self.factory = APIRequestFactory()

    def test_login(self):
        url = reverse('users:login')
        data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_create(self):
        url = reverse('users:list')
        self.another_user_data['password2'] = self.another_user_data['password']
        response = self.client.post(url, self.another_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'test2')
        self.assertEqual(User.objects.count(), 2)
        self.assertTrue(User.objects.filter(username='test2').exists())

    def test_user_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        users = User.objects.all()
        request = self.factory.get(url)
        serializer = UserListSerializer(
            users, many=True, context={'request': request}
        )
        self.assertEqual(response.data['results'], serializer.data)

    def test_user_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users:detail', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        request = self.factory.get(url)
        serializer = UserDetailSerializer(
            self.user, context={'request': request}
        )
        self.assertEqual(response.data, serializer.data)

    def test_email_confirm(self):
        self.user.is_active = False
        self.user.save()
        self.user.refresh_from_db()
        url = reverse('users:email-confirm')
        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(self.user.id)),
            'token': email_confirmation_token.make_token(self.user),
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['message'], 'Email confirmed with success.'
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_change_password(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users:change-password', args=[self.user.id])
        data = {
            'old_password': self.user_data['password'],
            'password': '4n0th3rp4ssw0rd',
            'password2': '4n0th3rp4ssw0rd'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['message'], 'Password updated successfully.'
        )

    def test_password_reset(self):
        url = reverse('users:password-reset')
        data = {'email': self.user_data['email']}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['message'],
            'We have sent you a link to reset your password.'
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, 'Django app password reset'
        )

    def test_password_reset_confirm(self):
        url = reverse('users:password-reset-confirm')
        data = {
            'uidb64': urlsafe_base64_encode(force_bytes(self.user.id)),
            'token': PasswordResetTokenGenerator().make_token(self.user),
            'password': '4n0th3rp4ssw0rd',
            'password2': '4n0th3rp4ssw0rd'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['message'], 'Password changed successfully.'
        )


