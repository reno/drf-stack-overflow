from django.contrib.auth import get_user_model
from django.test import TestCase
from users.tests.data import user_data
from users.tokens import email_confirmation_token


class TokensTestCase(TestCase):

    def setUp(self):
        UserModel = get_user_model()
        self.user = UserModel.objects.create_user(**user_data)
        self.token = email_confirmation_token.make_token(self.user)

    def test_encode(self):
        token = email_confirmation_token.make_token(self.user)
        self.assertEqual(self.token, token)

    def test_decode(self):
        self.assertTrue(email_confirmation_token.check_token(self.user, self.token))

