from django.contrib.auth import login
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from users.forms import CustomUserRegistrationForm
from users.models import CustomUser
from users.tokens import email_confirmation_token


# Move this view to your core app
class IndexView(TemplateView):
    template_name = 'core/index.html'


class UserRegistrationView(FormView):
    template_name = 'registration/registration_form.html'
    form_class = CustomUserRegistrationForm
    success_url = reverse_lazy('sign_up_done')

    def form_valid(self, form):
        form.cleaned_data['password'] = form.cleaned_data['password1']
        form.cleaned_data.pop('password1')
        form.cleaned_data.pop('password2')
        user = CustomUser.objects.create_user(**form.cleaned_data)
        domain = get_current_site(self.request)
        form.send_confirmation_email(user, domain)
        return super().form_valid(form)


class UserRegistrationDoneView(TemplateView):
    template_name = 'registration/registration_done.html'


class EmailConfirmView(View):

    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=id)
        except (TypeError, ValueError, OverflowError, ObjectDoesNotExist):
            user = None

        if user and email_confirmation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('index')
        else:
            return render(
                request,
                'registration/registration_confirm_invalid.html',
                status=400
            )