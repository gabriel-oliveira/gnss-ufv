from django.shortcuts import render
from .forms import simpleRelativo
from bernese.core.process_line import check_line
# from datetime import datetime, date
# from bernese.core import apiBernese, rinex, utils
# from threading import Thread
# from bernese.core.log import log
# import sys

def index(request):
	template_name = 'relativo/index.html'
	context = {}
	erroMsg = 'Erro(s):'
	context['isRelativo'] = True

	if request.method == 'POST':

		form = simpleRelativo(request.POST, request.FILES)

		if form.is_valid():

			form.save()

			check_line()

			context['isOK'] = True  # retorno ao usuario de solicitação enviada com sucesso
			form = simpleRelativo() # Novo formulário em branco

		else:

			context['isErro'] = True
			context['erroMsg'] = erroMsg

	else:

		form = simpleRelativo() # Novo formulário em branco

	context['form'] = form

	return render(request, template_name, context)
