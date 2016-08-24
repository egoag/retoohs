from django.conf.urls import url
from django.views.generic import TemplateView
from ss import views

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='ss/index.html'), name='index'),
    url(r'^create$', views.SSUserCreate.as_view(), name='create'),
    url(r'^invites/create$', views.InviteCodeCreate.as_view(), name='create_invite_code'),
    url(r'^invites', views.InviteCodeList.as_view(), name='invite_code_list'),
    url(r'^nodes$', views.NodeList.as_view(), name='node_list'),
]
