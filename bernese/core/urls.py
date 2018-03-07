from django.conf.urls import url
from bernese.core.views import index, about, contact, monitor, tools

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^ferramentas/$', tools, name='tools'),
    url(r'^sobre/$', about, name='about'),
    url(r'^contato/$', contact, name='contact'),
    url(r'^monitoramento/$', monitor, name='monitor'),
]
