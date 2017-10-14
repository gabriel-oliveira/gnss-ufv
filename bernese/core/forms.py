from django import forms
from django.core.mail import send_mail
from django.conf import settings
from bernese.settings import BASE_DIR
from bernese.core.mail import send_mail_template
from datetime import datetime
import threading

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

		# Salvando backup da mensagem no servidor
		msg_txt = 'Em: ' + datetime.now().isoformat(' ','seconds') + '\n'
		msg_txt += 'Nome: {name}\nE-mail: {email}\nMessage: {message}\n'.format(**context)

		with open(BASE_DIR + '/backupMsgContato.txt','a') as f:
		    print(msg_txt, file=f)


		# Enviando o email em um processamento paralelo
		threading.Thread(target=send_mail_template,
			args = (subject, template_name, context, [settings.CONTACT_EMAIL])
			).start()
