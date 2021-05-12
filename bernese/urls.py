"""bernese URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.conf.urls import url, include
from django.contrib import admin
from django.urls import path, include, reverse
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('controle/', admin.site.urls),
    path('', include('bernese.core.urls', namespace='core')),
    path('ppp/', include('bernese.ppp.urls', namespace='ppp')),
    path('relativo/', include('bernese.relativo.urls', namespace='relativo')),
    path('rapido/', include('bernese.rapido.urls', namespace='rapido')),
    path('rede/', include('bernese.rede.urls', namespace='rede')),
    path('conta/', include('bernese.accounts.urls', namespace='accounts')),
    path('favicon.ico',RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('robots.txt',RedirectView.as_view(url='/static/robots.txt',permanent=True)),
    path('apple-touch-icon-precomposed.png',RedirectView.as_view(url='/static/logo-gnss-ufv.png', permanent=True)),
    path('apple-touch-icon.png',RedirectView.as_view(url='/static/logo-gnss-ufv.png', permanent=True))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# handler500 = 'bernese.core.views.custom_error_500_view'
