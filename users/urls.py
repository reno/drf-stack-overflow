from django.urls import path, include
from users.views import UserRegistrationView, UserRegistrationDoneView, EmailConfirmView

urlpatterns = [
    # User registration urls
    path('signup/', UserRegistrationView.as_view(), name='sign_up'),
    path('signup/done/', UserRegistrationDoneView.as_view(), name='sign_up_done'),
    path('email-confirm/<uidb64>/<token>/', EmailConfirmView.as_view(),
         name='email_confirm'),
    # Default Django auth urls
    # https://github.com/django/django/blob/main/django/contrib/auth/urls.py
    path('', include('django.contrib.auth.urls')),
    # Include the following urls:
    # /login/ [name='login']
    # /logout/ [name='logout']
    # /password_change/ [name='password_change']
    # /password_change/done/ [name='password_change_done']
    # /password_reset/ [name='password_reset']
    # /password_reset/done/ [name='password_reset_done']
    # /reset/<uidb64>/<token>/ [name='password_reset_confirm']
    # /reset/done/ [name='password_reset_complete']
]