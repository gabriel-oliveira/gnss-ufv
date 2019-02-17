# from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views
from bernese.accounts.forms import AuthenticationForm2
from .views import register, register_validator
from django.urls import reverse_lazy

app_name='accounts'

urlpatterns = [
    path('entrar/', views.LoginView.as_view(template_name='login.html',
                                            form_class=AuthenticationForm2,
                                            redirect_authenticated_user=True),
                    name='login'),

    path('sair/', views.LogoutView.as_view(next_page='core:index'), name='logout'),
    path('cadastrar/', register, name='register'),
    path('alterar-senha/',views.PasswordResetView.as_view(
                                            template_name='password_reset.html',
                                            success_url='ok/',
                                            email_template_name = 'password_reset_email.html'
                        ),name='password_reset'),
    path('nova-senha/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(
                                            template_name='password_reset_confirm.html',
                                            success_url=reverse_lazy('accounts:password_reset_complete')
                        ), name='password_reset_confirm'),
    path('alterar-senha/ok/',views.PasswordResetDoneView.as_view(
                                            template_name='password_reset_done.html'
                        ),name='password_reset_done'),
    path('nova-senha/ok/',views.PasswordResetCompleteView.as_view(
                                            template_name='password_reset_complete.html'
                        ),name='password_reset_complete'),
    path('cadastrar/<uidb64>/<token>/', register_validator, name='register_validator'),

]
