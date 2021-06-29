from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from users.models import CustomUser
from users.tests.data import user_data, user_form_data
from users.tokens import email_confirmation_token


class ViewsTestCase(TestCase):

    def test_user_registration_view_get(self):
        url = reverse('sign_up')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration_form.html')

    def test_user_registration_view_post(self):
        url = reverse('sign_up')
        response = self.client.post(url, data=user_form_data, follow=True)
        UserModel = get_user_model()
        user = UserModel.objects.get(username=user_form_data['username'])
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(user, CustomUser))
        self.assertTemplateUsed('registration/registration_done.html')
        self.assertEqual(len(mail.outbox), 1)

    def test_email_confirm_view(self):
        UserModel = get_user_model()
        user = UserModel.objects.create_user(**user_data)
        self.assertFalse(user.is_active)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_confirmation_token.make_token(user)
        url = reverse('email_confirm', args=[uidb64, token])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)






