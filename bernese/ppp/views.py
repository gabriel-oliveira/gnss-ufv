from django.shortcuts import render
from .forms import simplePPP
from datetime import datetime
from bernese.core.apiBernese import *
from bernese.core.rinex import *
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

			f = request.FILES['rinexFile']

			(f_isOK,erroMsg) = isRinex(f)

			if f_isOK: (f_isOK,erroMsg,header,pathTempFile) = readRinexObs(f)

			if f_isOK:

				bpeName = 'bern' + '{:03d}'.format(datetime.now().timetuple().tm_yday)
				bpeName += '_' +  '{:02d}'.format(datetime.now().timetuple().tm_hour)
				bpeName += '{:02d}'.format(datetime.now().timetuple().tm_min)
				bpeName += '{:02d}'.format(datetime.now().timetuple().tm_sec)

				header['ID'] = 1
				header['ID2'] = header['MARKER NAME'][:2]
				header['FLAG'] = ''
				header['PLATE'] = form.cleaned_data['plate']

				headers = [header]
				pathTempFiles = [pathTempFile]

				try:

					# Nova instancia da API para o Bernese
					pppBPE = ApiBernese(bpeName,headers,form.cleaned_data['email'],pathTempFiles)

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
