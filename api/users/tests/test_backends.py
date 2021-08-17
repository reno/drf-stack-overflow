import json
import os
from django.contrib.auth import get_user_model, authenticate
from django.test import TestCase


class CustomBackendTestCase(TestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'data.json')
        with open(file_path) as file:
            data = json.load(file)
        self.user_data = data.get('user_data')
        User = get_user_model()
        self.user = User.objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()

    def test_authenticate_username(self):
        self.assertEqual(
            authenticate(
                username=self.user_data['username'],
                password=self.user_data['password']
            ),
            self.user
        )

    def test_authenticate_email(self):
        self.assertEqual(
            authenticate(
                username=self.user_data['email'],
                password=self.user_data['password']
            ),
            self.user
        )

    def test_authenticate_fail(self):
        self.assertFalse(
            authenticate(
                username='Something',
                password=self.user_data['password']
            )
        )
