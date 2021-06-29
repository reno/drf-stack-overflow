from django.contrib.auth.forms import UserCreationForm
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from users.models import CustomUser
from users.tokens import email_confirmation_token


class CustomUserRegistrationForm(UserCreationForm):

    class Meta():
        model = CustomUser
        fields = (
            'email', 'first_name', 'last_name', 'username', 'password1', 'password2'
        )

    def send_confirmation_email(self, user, domain):
        subject = 'Django app account verification'
        context = {
            'user': user,
            'domain': domain,
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': email_confirmation_token.make_token(user),
        }
        message = render_to_string(
            'registration/registration_confirm_email.html', context
        )
        user.email_user(subject, message)