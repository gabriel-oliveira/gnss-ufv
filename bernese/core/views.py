from django.shortcuts import render
from .forms import ContactGeneral
from .mail import enviar_email
# from django.http import HttpResponse

# Create your views here.
def index(request):
	# return HttpResponse('Em construção!')
	template_name = 'index.html'
	context = {}
	context['isHome'] = True
	return render(request, template_name, context)

def about(request):
	template_name = 'about.html'
	context = {}
	context['isAbout'] = True
	return render(request, template_name, context)

def contact(request):
	template_name = 'contact.html'
	context = {}
	if request.method == 'POST':
		form = ContactGeneral(request.POST)
		if form.is_valid():
			context['is_valid'] = True
			email_context = {
				'name' : form.cleaned_data['name'],
				'email' : form.cleaned_data['email'],
				'message' : form.cleaned_data['message'],
			}
			enviar_email(**email_context)
			form = ContactGeneral()
	else:
		form = ContactGeneral()

	context['form'] = form
	context['isContact'] = True
	return render(request, template_name, context)
