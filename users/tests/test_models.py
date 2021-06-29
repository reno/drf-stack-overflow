from django.contrib.auth import get_user_model
from django.test import TestCase
from users.models import CustomUser
from users.tests.data import user_data


class CustomUserTestCase(TestCase):

    def setUp(self):
        UserModel = get_user_model()
        self.user = UserModel.objects.create(**user_data)

    def test_type(self):
        self.assertTrue(isinstance(self.user, CustomUser))

    def test_str(self):
        self.assertEqual(self.user.__str__(), self.user.username)

    def test_get_full_name(self):
        self.assertEqual(
            self.user.get_full_name,
            f'{self.user.first_name} {self.user.last_name}'
        )


class CustomUserManagerTestCase(TestCase):

    def test_create_user(self):
        UserModel = get_user_model()
        user = UserModel.objects.create_user(**user_data)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        UserModel = get_user_model()
        user = UserModel.objects.create_superuser(**user_data)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
