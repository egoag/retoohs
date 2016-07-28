from django.conf.urls import url
from ss import views

urlpatterns = [
    url(r'^create$', views.SSUserCreate.as_view(), name='create'),
]
