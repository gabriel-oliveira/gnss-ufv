import django
from os import environ, getenv

e = environ.setdefault('DJANGO_SETTINGS_MODULE','bernese.settings')

django.setup()

from bernese.accounts.models import MyUser

try:

    su = MyUser()
    su.email=getenv('ADMIN_EMAIL','teste@teste.com')
    su.first_name='Admin'
    su.observacao='Superuser'
    su.is_active=True
    su.is_admin=True
    su.set_password(getenv('ADMIN_PASSWORD','123456'))
    su.save()
    print('Superuser Created')
except Exception as e:
    print(e)
