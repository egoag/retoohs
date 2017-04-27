import datetime
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.core.mail import send_mail
from django.views import generic
from django.utils import timezone
from django.conf import settings
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .forms import LoginForm, RegisterForm
from .serializers import ChangeEmailSerializer, DeleteMyAccountSerializer
from main.models import User, EmailVerification


class Register(generic.CreateView):
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('ss:index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse_lazy('ss:index'))
        return super(Register, self).dispatch(request, *args, **kwargs)


def login(request):
    redirect_to = request.POST.get('next', request.GET.get('next', '/dashboard'))
    if not request.user.is_anonymous():
        if not is_safe_url(url=redirect_to, host=request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
        return HttpResponseRedirect(redirect_to)
    if request.method == "POST":
        form = LoginForm(request, redirect_to=redirect_to, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
    else:
        form = LoginForm(request, redirect_to=redirect_to)

    current_site = get_current_site(request)

    context = {
        'form': form,
        'next': redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }

    return TemplateResponse(request, 'login.html', context)


def logout(request):
    auth_logout(request)

    if 'next' in request.POST or 'next' in request.GET:
        next_page = request.POST.get('next', request.GET.get('next'))
        if not is_safe_url(url=next_page, host=request.get_host()):
            return HttpResponseRedirect(request.path)
        else:
            return HttpResponseRedirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': 'Logged out'
    }

    return TemplateResponse(request, 'logout.html', context)


class UserInfo(LoginRequiredMixin, generic.DetailView):
    template_name = 'main/user_detail.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(UserInfo, self).get_context_data(**kwargs)
        context.update({'page_msg': 'My Info', 'page_header': '我的信息'})
        return context


def verify_email(request, code):
    if not request.user.is_anonymous():
        HttpResponseRedirect('/dashboard')

    try:
        email_verification = EmailVerification.objects.get(code=code)
    except EmailVerification.DoesNotExist:
        context = {
            'error': 'Email verify failed, verification code is not correct.'
        }
    else:
        if email_verification.time_created < timezone.now() - datetime.timedelta(
                hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS):
            context = {
                'error': 'Email verify failed, verification code has expired.'
            }
        else:
            email_verification.user.email_verified = True
            email_verification.user.save()
            email_verification.delete()
            context = {
                'success': 'Email verify successfully, please log in.'
            }
    return TemplateResponse(request, 'main/email_verification.html', context)


class UserUpdateEmail(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangeEmailSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        instance = serializer.save()
        EmailVerification.objects.filter(user=instance).delete()  # otherwise user can register others email
        email_verification = EmailVerification.objects.create(user=instance)
        message = render_to_string('main/email_verification_email.html', context={
            'site_name': 'retoohs',
            'username': instance.username,
            'active_link': settings.EMAIL_VERIFICATION_URL.format(email_verification.code),
        })
        send_mail(
            'Active your account',
            message,
            settings.EMAIL_SENDER,
            [instance.email],
        )
        instance.email_verified = False
        instance.save()  # set not email verified

    def post(self, request, *args, **kwargs):
        return super(UserUpdateEmail, self).update(request, *args, **kwargs)


def resend_email(request):
    if not request.user.is_authenticated():
        return JsonResponse({'error': 'Please log in first.'})

    if request.user.email_verified:
        return JsonResponse({'error': 'Email already verified.'})

    email_verification = EmailVerification.objects.create(user=request.user)
    message = render_to_string('main/email_verification_email.html', context={
        'site_name': 'retoohs',
        'username': request.user.username,
        'active_link': settings.EMAIL_VERIFICATION_URL.format(email_verification.code),
    })
    send_mail(
        'Active your account',
        message,
        settings.EMAIL_SENDER,
        [request.user.email],
    )
    return JsonResponse({'ok': True})


class DeleteMyAccount(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        return super(DeleteMyAccount, self).destroy(request, *args, **kwargs)
