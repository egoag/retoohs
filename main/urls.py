from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_view
from . import views
from . import forms

urlpatterns = [
    url(r'^register$', views.Register.as_view(), name='register'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^donate$', TemplateView.as_view(template_name='main/donate.html'), name='donate'),
    url(r'^my$', views.UserInfo.as_view(), name='my'),
    url(r'^email-verify/(?P<code>[0-9a-zA-Z]+)$', views.verify_email, name='email_verify'),
    url(r'^email-change$', views.UserUpdateEmail.as_view(), name='email_change'),
    url(r'^email-resend$', views.resend_email, name='email_resend'),
    url(r'^destroy-account$', views.DeleteMyAccount.as_view(), name='destroy_account'),

    # auth views
    url(r'^password_change/$',
        auth_view.password_change,
        {
            'template_name': 'main/password_change_form.html',
            'password_change_form': forms.PasswordChangeForm,
        },
        name='password_change'),
    url(r'^password_change/done/$',
        auth_view.password_change_done,
        {'template_name': 'main/password_change_done.html'},
        name='password_change_done'),
    url(r'^password_reset/$',
        auth_view.password_reset,
        {'template_name': 'main/password_reset_form.html',
         'password_reset_form': forms.PasswordResetForm
         },
        name='password_reset'),
    url(r'^password_reset/done/$',
        auth_view.password_reset_done,
        {'template_name': 'main/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_view.password_reset_confirm,
        {'template_name': 'main/password_reset_confirm.html',
         'set_password_form': forms.SetPasswordForm},
        name='password_reset_confirm'),
    url(r'^reset/done/$',
        auth_view.password_reset_complete,
        {'template_name': 'main/password_reset_complete.html'},
        name='password_reset_complete'),
]
