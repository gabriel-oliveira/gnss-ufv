from django.shortcuts import render
from .forms import simplePPP
from os import path
from datetime import datetime
from bernese.core.apiBernese import *
from bernese.core.rinex import *
from threading import Thread

def index(request):
	template_name = 'ppp/index.html'
	context = {}
	context['isPPP'] = True

	if request.method == 'POST':

		form = simplePPP(request.POST, request.FILES)

		if form.is_valid():

			f = request.FILES['rinexFile']

			(status,erroMsg) = isRinex(f)

			if status: (status,erroMsg,header,pathTempFile) = readRinexObs(f)

			if status:

				bpeName = 'bern' + '{:03d}'.format(datetime.now().timetuple().tm_yday)
				bpeName += '_' +  '{:02d}'.format(datetime.now().timetuple().tm_hour)
				bpeName += '{:02d}'.format(datetime.now().timetuple().tm_min)
				bpeName += '{:02d}'.format(datetime.now().timetuple().tm_sec)

				pppBPE = ApiBernese(bpeName,header,form.cleaned_data['email'],pathTempFile)
				Thread(name=bpeName,target=pppBPE.runBPE).start()

				context['isOK'] = True
				form = simplePPP()

			else:
				context['isErro'] = True
				context['erroMsg'] = erroMsg

	else:
		form = simplePPP()

	context['form'] = form

	return render(request, template_name, context)
