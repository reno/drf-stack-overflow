from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from users.tokens import email_confirmation_token


def send_email(user, domain, token, subject, template):
    context = {
        'user': user,
        'domain': domain,
        'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token.make_token(user),
    }
    message = render_to_string(template, context)
    user.email_user(subject, message)


def send_confirmation_email(user, domain):
    token = email_confirmation_token
    subject = 'Django app account verification'
    template = 'confirmation_email.html'
    send_email(user, domain, token, subject, template)


def send_password_reset_email(user, domain):
    token = PasswordResetTokenGenerator()
    subject = 'Django app password reset'
    template = 'password_reset_email.html'
    send_email(user, domain, token, subject, template)

