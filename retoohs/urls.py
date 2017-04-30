"""retoohs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from django.contrib import admin

urlpatterns = [
    url('^$', TemplateView.as_view(template_name='index.html'), name='index'),
    # url('^avatar/', include('avatar.urls')),
    url(r'^{}/'.format(getattr(settings, 'ADMIN_URL', 'admin')), admin.site.urls),
    url(r'^dashboard/forums/', include('lbforum.urls')),
    url(r'^dashboard/', include('ss.urls', namespace='ss')),
    url(r'^', include('main.urls')),
    url(r'^attachments/', include('lbattachment.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
