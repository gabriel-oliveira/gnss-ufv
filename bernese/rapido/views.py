from django.shortcuts import render
from .forms import rapidoRelativo
from bernese.core.process_line import check_line
from django.contrib.auth.decorators import login_required
import requests

@login_required
def index(request):
	template_name = 'rapido/index.html'
	context = {}
	erroMsg = 'Erro(s):'
	context['isRelativo'] = True

	if request.method == 'POST':

		form = rapidoRelativo(request.POST, request.FILES)

		if form.is_valid():

			form.save()

			context['isOK'] = True  # retorno ao usuario de solicitação enviada com sucesso
			form = rapidoRelativo() # Novo formulário em branco

		else:

			context['isErro'] = True
			context['erroMsg'] = erroMsg

	else:

		form = rapidoRelativo() # Novo formulário em branco

	context['form'] = form

	return render(request, template_name, context)
