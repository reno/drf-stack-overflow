from django.contrib import admin
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(UserManager):
    '''Custom user manager. Extends the default UserManager.'''

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return super()._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return super()._create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    '''Custom user model.

    CustomUser inherits the following fields from AbstractUser:
    username, first_name, last_name, date_joined, last_login, is_staff, is_superuser
    '''
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages = {'unique': _('This email is already registered.')},
    )
    is_active = models.BooleanField(_('active'), default=False)
    picture = models.ImageField(
        _('Profile picture'), upload_to='profile_pics/', null=True, blank=True
    )
    location = models.CharField(
        _('Location'), max_length=50, null=True, blank=True
    )
    job_title = models.CharField(
        _('Job title'), max_length=50, null=True, blank=True
    )
    bio = models.CharField(_('Bio'), max_length=280, blank=True, null=True)
    website_url = models.URLField(
        _('Website link'), max_length=555, blank=True, null=True
    )
    twitter_account = models.URLField(
        _('Twitter account'), max_length=255, blank=True, null=True
    )
    github_account = models.URLField(
        _('GitHub profile'), max_length=255, blank=True, null=True
    )
    objects = CustomUserManager()

    class Meta:
        ordering = ['id']
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.username

    @property
    @admin.display(description=_('name'))
    def get_full_name(self):
        '''Overwrites method as property.'''
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name:
            return self.first_name
        else:
            return ''
