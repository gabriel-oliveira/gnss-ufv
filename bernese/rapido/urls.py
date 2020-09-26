# from django.conf.urls import url
from django.urls import path
from bernese.rapido.views import index

app_name='rapido'

urlpatterns = [
    path('', index, name='index'),
]
