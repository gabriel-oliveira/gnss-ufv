#from django.conf.urls import url
from django.urls import path
from bernese.core.views import index, about, contact, monitor, tools, check

app_name = 'core'

urlpatterns = [
    path('', index, name='index'),
    path('ferramentas/', tools, name='tools'),
    path('sobre/', about, name='about'),
    path('contato/', contact, name='contact'),
    path('monitoramento/', monitor, name='monitor'),
    path('check/',check, name='check')
]
