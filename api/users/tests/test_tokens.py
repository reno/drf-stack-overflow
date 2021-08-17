import json
import os
from django.contrib.auth import get_user_model
from django.test import TestCase
from users.tokens import email_confirmation_token


class TokensTestCase(TestCase):

    def setUp(self):
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, 'data.json')
        with open(file_path) as file:
            data = json.load(file)
        user_data = data.get('user_data')
        UserModel = get_user_model()
        self.user = UserModel.objects.create_user(**user_data)
        self.token = email_confirmation_token.make_token(self.user)

    def test_encode(self):
        token = email_confirmation_token.make_token(self.user)
        self.assertEqual(self.token, token)

    def test_decode(self):
        self.assertTrue(email_confirmation_token.check_token(self.user, self.token))

