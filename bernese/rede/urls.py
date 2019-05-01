# from django.conf.urls import url
from django.urls import path
from bernese.rede.views import index

app_name='rede'

urlpatterns = [
    path('', index, name='index'),
]
