# from django.conf.urls import url
from django.urls import path
from bernese.ppp.views import index

app_name='ppp'

urlpatterns = [
    path('', index, name='index'),
]
