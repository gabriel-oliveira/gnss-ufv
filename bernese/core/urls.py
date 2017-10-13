from django.conf.urls import url
from bernese.core.views import index, about, contact

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^sobre/$', about, name='about'),
    url(r'^contato/$', contact, name='contact'),
]
