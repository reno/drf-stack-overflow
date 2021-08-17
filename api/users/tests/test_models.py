import json
import os
from django.contrib.auth import get_user_model
from django.test import TestCase
from users.models import CustomUser

User = get_user_model()


class CustomUserTestCase(TestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'data.json')
        with open(file_path) as file:
            data = json.load(file)
        user_data = data.get('user_data')
        self.user = User.objects.create(**user_data)

    def test_type(self):
        self.assertTrue(isinstance(self.user, CustomUser))

    def test_str(self):
        self.assertEqual(self.user.__str__(), self.user.username)

    def test_get_full_name(self):
        self.assertEqual(
            self.user.get_full_name,
            f'{self.user.first_name} {self.user.last_name}'
        )

    def test_get_full_name_first_only(self):
        self.user.last_name = ''
        self.user.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.get_full_name, f'{self.user.first_name}')

    def test_get_full_name_blank(self):
        self.user.first_name = ''
        self.user.last_name = ''
        self.user.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.get_full_name, '')


class CustomUserManagerTestCase(TestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'data.json')
        with open(file_path) as file:
            data = json.load(file)
        self.user_data = data.get('user_data')

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = User.objects.create_superuser(**self.user_data)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
