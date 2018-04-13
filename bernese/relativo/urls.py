# from django.conf.urls import url
from django.urls import path
from bernese.relativo.views import index

app_name='relativo'

urlpatterns = [
    path('', index, name='index'),
]
