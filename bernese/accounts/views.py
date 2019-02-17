from django.shortcuts import render
from .forms import MyUserCreationForm
from .utils import send_newuser_mail, register_validator as register_isValid
from django.http import HttpResponse

def register(request):
    template_name = 'register.html'
    isSuccess = False

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            usermail = form.cleaned_data['email']

            # envia e-mail para os administradores com botão (link) para validar cadastro
            send_newuser_mail(usermail, request)

            form = MyUserCreationForm()
            isSuccess = True

    else:
        form = MyUserCreationForm()
        isSuccess = False

    context = {
        'form' : form,
        'isSuccess' : isSuccess
    }

    return render(request, template_name, context)

def register_validator(request,uidb64,token):
    template_name = 'register_validator.html'
    context = {
        'isSuccess' : register_isValid(uidb64,token)
    }
    return render(request, template_name, context)
