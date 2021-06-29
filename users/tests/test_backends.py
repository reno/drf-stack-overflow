from django.contrib.auth import get_user_model, authenticate
from django.test import TestCase
from users.tests.data import user_data as data


class CustomBackendTestCase(TestCase):

    def setUp(self):
        UserModel = get_user_model()
        self.user = UserModel.objects.create_user(**data)
        self.user.is_active = True
        self.user.save()

    def test_authenticate_username(self):
        self.assertEqual(
            authenticate(username=data['username'], password=data['password']),
            self.user
        )

    def test_authenticate_email(self):
        self.assertEqual(
            authenticate(username=data['email'],password=data['password']),
            self.user
        )

    def test_authenticate_fail(self):
        self.assertFalse(
            authenticate(username='Something', password=data['password'])
        )
