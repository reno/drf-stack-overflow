from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):
    '''Generate one-time token based on email confirmation.'''

    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{user.password}{timestamp}{user.is_active}'

email_confirmation_token = EmailConfirmationTokenGenerator()