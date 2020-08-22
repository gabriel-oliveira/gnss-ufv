from django.shortcuts import render
from .forms import simplePPP
import requests
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import requests

@login_required
def index(request):

	template_name = 'ppp/index.html'
	context = {}
	erroMsg = 'Erro(s):'
	context['isPPP'] = True

	if request.method == 'POST':

		form = simplePPP(request.POST, request.FILES)

		if form.is_valid():

			form.save()

			context['isOK'] = True  # retorno ao usuario de solicitação enviada com sucesso
			form = simplePPP()      # Novo formulário em branco

		else:

			context['isErro'] = True
			context['erroMsg'] = erroMsg

	else:
		form = simplePPP()

	context['form'] = form

	return render(request, template_name, context)
