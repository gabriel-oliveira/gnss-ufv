from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm
from .models import MyUser

class AuthenticationForm2(AuthenticationForm):
    username = UsernameField(
        label="E-mail",
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        )


class MyUserCreationForm(UserCreationForm):

    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirmação da Senha', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if MyUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Este e-mail já está cadastrado.')
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Confirmação de senha não confere!")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


    class Meta(UserCreationForm.Meta):
        model = MyUser
        fields = ('email', 'first_name', 'last_name', 'matricula', 'password1', 'password2','observacao')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            # 'password1': forms.TextInput(attrs={'class': 'form-control'}),
            # 'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'placeholder':
            'Decreva acerca de seu interesse pelo sistema.'}),
        }
