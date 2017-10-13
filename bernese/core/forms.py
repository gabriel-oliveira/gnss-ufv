from django import forms
from django.core.mail import send_mail
from django.conf import settings

from bernese.core.mail import send_mail_template

class ContactGeneral(forms.Form):

	name = forms.CharField(
		label = 'Nome',
		widget = forms.TextInput(attrs={'class': 'form-control'})
		)

	email = forms.EmailField(
		label='Email',
		widget = forms.EmailInput(
			attrs={'class': 'form-control'}
				)
		)

	message = forms.CharField(
		label = 'Mensagem/Sugestão',
		widget = forms.Textarea(attrs={'class': 'form-control'})
		)

	def enviar_email(self):
		subject = 'Contato'
		context = {
			'name': self.cleaned_data['name'],
			'email': self.cleaned_data['email'],
			'message': self.cleaned_data['message'],
		}
		template_name = 'contact_email.html'

		send_mail_template(subject, template_name, context, [settings.CONTACT_EMAIL])
