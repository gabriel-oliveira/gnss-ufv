from django.template.loader import render_to_string
from django.template.defaultfilters import striptags
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf.settings import DEFAULT_FROM_MAIL, CONTACT_EMAIL


def send_mail_template(subject, template_name, context, recipient_list,
	from_email=DEFAULT_FROM_MAIL, fail_silently=False):

	message_html = render_to_string(template_name, context)

	message_txt = striptags(message_html)

	email = EmailMultiAlternatives(subject=subject, body=message_txt, from_email=from_email, to=recipient_list)
	email.attach_alternative(message_html, "text/html")
	email.send(fail_silently=fail_silently)


def enviar_email(name,email,message):
	subject = 'Contato'
	context = {
		'name': name,
		'email': email,
		'message': message,
	}
	template_name = 'contact_email.html'


	# Salvando backup da mensagem no servidor
	msg_txt = 'Em: ' + datetime.now().isoformat(' ','seconds') + '\n'
	msg_txt += 'Nome: {name}\nE-mail: {email}\nMessage: {message}\n'.format(**context)

	with open(BASE_DIR + '/backupMsgContato.txt','a') as f:
	    print(msg_txt, file=f)


	# Enviando o email em um processamento paralelo
	Thread(target=send_mail_template,
		args = (subject, template_name, context, [CONTACT_EMAIL])
		).start()
