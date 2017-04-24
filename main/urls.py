from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

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
]
