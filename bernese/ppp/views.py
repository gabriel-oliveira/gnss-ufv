from django.shortcuts import render
from .forms import simplePPP
from datetime import datetime
from bernese.core.apiBernese import *
from bernese.core.rinex import *
from bernese.core.utils import *
from threading import Thread
from bernese.core.log import log
import sys

def index(request):
	template_name = 'ppp/index.html'
	context = {}
	erroMsg = 'Erro'
	context['isPPP'] = True

	if request.method == 'POST':

		form = simplePPP(request.POST, request.FILES)

		if form.is_valid():

			# Define o nome (id) do processamento
			bpeName = setBernID()

			# print(request.FILES)
			f = request.FILES['rinexFile']

			if 'blqFile' in request.FILES:
				b = request.FILES['blqFile']
			else:
				b = False

			(f_isOK,erroMsg) = isRinex(f)

			if f_isOK: (f_isOK,erroMsg,header,pathTempFile) = readRinexObs(f,bpeName)

			if f_isOK and b:
				(f_isOK,erroMsg,pathBlqTempFile) = saveBlq(b,bpeName)

			if f_isOK:

				# if form.cleaned_data['blqCheck']:
				# 	header['BLQ'] = 'SYSTEM'
				# else:
				# 	header['BLQ'] = 'USER'
				#
				# print(form.cleaned_data['blqCheck'])
				# print(type(form.cleaned_data['blqCheck'])
				# print(header['BLQ'])

				header['ID'] = 1
				header['ID2'] = header['MARKER NAME'][:2]
				header['FLAG'] = ''
				header['PLATE'] = form.cleaned_data['plate']

				headers = [header]
				pathTempFiles = [pathTempFile]
				pathBlqTempFiles = []
				if b: pathBlqTempFiles = [pathBlqTempFile]

				try:

					# Nova instancia da API para o Bernese
					pppBPE = ApiBernese(bpeName,headers,form.cleaned_data['email'],pathTempFiles,pathBlqTempFiles)

					# Abrindo novo processo para a solicitação
					Thread(name=bpeName,target=pppBPE.runBPE,kwargs={'prcType': 'PPP'}).start()

					context['isOK'] = True  # retorno ao usuario de solicitação enviada com sucesso
					form = simplePPP()      # Novo formulário em branco

				except Exception as e:

					context['isErro'] = True
					context['erroMsg'] = "Erro ao solicitar processamento. Por favor tente novamente."

					log('Erro ao solicitar processamento: ' + bpeName)
					e_Msg = sys.exc_info()
					log(str(e_Msg[0]))
					log(str(e_Msg[1]))

			else:
				context['isErro'] = True
				context['erroMsg'] = erroMsg

	else:
		form = simplePPP()

	context['form'] = form

	return render(request, template_name, context)
