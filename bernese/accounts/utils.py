from .models import MyUser
from django.contrib.auth.tokens import default_token_generator as TokenGenerator
from bernese.settings import ADMINS
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse

def send_newuser_mail(email, request):
    user = MyUser.objects.get(email=email)
    token = TokenGenerator.make_token(user)
    uidb64 = urlsafe_base64_encode(str(user.pk).encode()).decode()
    url = reverse('accounts:register_validator', kwargs={'uidb64': uidb64, 'token': token})
    mensagem = '''
    E-mail: {}
    Nome: {}
    Sobrenome: {}
    Matricula: {}
    Observação: {}
    {}'''.format(user.email,user.first_name,user.last_name,user.matricula,
                 user.observacao,request.build_absolute_uri(url))
    subject = '[GNSS-UFV] Validar Usuario'
    send_mail(subject, mensagem,
    'gnss.ufv@gmail.com', ADMINS, fail_silently=False)


def register_validator(uidb64,token):
    user = get_user(uidb64)
    token_isValid = TokenGenerator.check_token(user,token)
    if token_isValid:
        try:
            user.is_active = True
            user.save()
            status = True
            subject = '[GNSS-UFV] Cadastro validado com sucesso'
            send_mail(subject, ' ', 'gnss.ufv@gmail.com', [user.email], fail_silently=False)
        except:
            return False
    else:
        return False
        # TODO: email para usuario explicando o porque
    return True


def get_user(uidb64):
    try:
        # urlsafe_base64_decode() decodes to bytestring
        uid = urlsafe_base64_decode(uidb64).decode()
        user = MyUser.objects.get(pk=uid)
    except: #(TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
        user = None
    return user
