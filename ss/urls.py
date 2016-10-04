from django.conf.urls import url
from ss import views

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^check-in$', views.CheckIn.as_view(), name='check_in'),
    url(r'^create$', views.SSUserCreate.as_view(), name='create'),
    url(r'^invites/create$', views.InviteCodeCreate.as_view(), name='create_invite_code'),
    url(r'^invites', views.InviteCodeList.as_view(), name='invite_code_list'),
    url(r'^nodes$', views.NodeList.as_view(), name='node_list'),
    url(r'^nodes/create$', views.NodeCreate.as_view(), name='node_create'),
]
