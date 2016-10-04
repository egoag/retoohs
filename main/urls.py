from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^register$', views.Register.as_view(), name='register'),
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^my$', views.UserInfo.as_view(), name='my'),
]
