from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.utils.http import is_safe_url
from django.shortcuts import resolve_url
from django.conf import settings
from .forms import LoginForm


def login(request):
    redirect_to = request.POST.get('next', request.GET.get('next', ''))
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