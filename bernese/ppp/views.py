from django.shortcuts import render
from .forms import simplePPP
from bernese.core.process_line import check_line
# from bernese.core.rinex import *
# from bernese.core.utils import *
# from threading import Thread
# from bernese.core.log import log
# import sys


def index(request):
	template_name = 'ppp/index.html'
	context = {}
	erroMsg = 'Erro(s):'
	context['isPPP'] = True

	if request.method == 'POST':

		form = simplePPP(request.POST, request.FILES)

		if form.is_valid():

			form.save()

			check_line()

			context['isOK'] = True  # retorno ao usuario de solicitação enviada com sucesso
			form = simplePPP()      # Novo formulário em branco

		else:

			context['isErro'] = True
			context['erroMsg'] = erroMsg

	else:
		form = simplePPP()

	context['form'] = form

	return render(request, template_name, context)
