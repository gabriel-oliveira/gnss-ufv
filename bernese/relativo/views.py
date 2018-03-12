from django.shortcuts import render
from .forms import simpleRelative
from datetime import datetime, date
from bernese.core.apiBernese import *
from bernese.core.rinex import *
from threading import Thread
from bernese.core.log import log
import sys

def index(request):
	template_name = 'relativo/index.html'
	context = {}
	erroMsg = 'Erro desconhecido.'
	context['isRelativo'] = True
	f_isOK = False

	if request.method == 'POST':

		form = simpleRelative(request.POST, request.FILES)

		if form.is_valid():

			f_Base = request.FILES['rinexBaseFile']
			f_Rover = request.FILES['rinexRoverFile']

			(b_isOK,erroMsg) = isRinex(f_Base)
			(r_isOK,erroMsg) = isRinex(f_Rover)

			if (b_isOK and r_isOK):

				# Lendo Rinex Base
				(b_isOK,erroMsg,b_header,b_pathTempFile) = readRinexObs(f_Base)

				if b_isOK:

					b_header['ID'] = 1
					b_header['ID2'] = b_header['MARKER NAME'][:2]
					b_header['FLAG'] = 'B'
					b_header['PLATE'] = form.cleaned_data['plateBase']

					# Definindo coordenada da base informada pelo usuario
					if request.POST['choice_coord_from'] == 'COORD_USER_DEFINED':

						b_header['APPROX POSITION XYZ'][0] = float(request.POST['coord_X'])
						b_header['APPROX POSITION XYZ'][1] = float(request.POST['coord_Y'])
						b_header['APPROX POSITION XYZ'][2] = float(request.POST['coord_Z'])

					# Lendo Rinex Rover
					(r_isOK,erroMsg,r_header,r_pathTempFile) = readRinexObs(f_Rover)

					if r_isOK:

						f_isOK = True    # Arquivos Rinex lidos e validados

						r_header['ID'] = 2
						r_header['FLAG'] = ''
						r_header['ID2'] = ''
						r_header['PLATE'] = form.cleaned_data['plateRover']

						# Define two char ABBreviation
						if r_header['MARKER NAME'][:2] != b_header['MARKER NAME'][:2]:
							r_header['ID2'] = r_header['MARKER NAME'][:2] # 1° and 2°
						elif r_header['MARKER NAME'][0::2] != b_header['MARKER NAME'][:2]:
							r_header['ID2'] = r_header['MARKER NAME'][0::2] # 1° and 3°
						elif r_header['MARKER NAME'][0::3] != b_header['MARKER NAME'][:2]:
							r_header['ID2'] = r_header['MARKER NAME'][0::3] # 1° and 4°
						else:
							for i in range(0,10):
								if (r_header['MARKER NAME'][0] + str(i)) != b_header['MARKER NAME'][:2]:
									r_header['ID2'] = (r_header['MARKER NAME'][0] + str(i))
									break

						# Verificando se os dois arquivos são do mesmo dia
						b_Date = b_header['TIME OF FIRST OBS'].split()
						b_day = date(year=int(b_Date[0]),month=int(b_Date[1]),day=int(b_Date[2]))
						r_Date = r_header['TIME OF FIRST OBS'].split()
						r_day = date(year=int(r_Date[0]),month=int(r_Date[1]),day=int(r_Date[2]))

						if b_day != r_day:
							f_isOK = False
							erroMsg = 'Arquivos não são do mesmo dia.'

						if r_header['MARKER NAME'] == b_header['MARKER NAME']:
							f_isOK = False
							erroMsg = 'Arquivos da mesma estação (' + b_header['MARKER NAME'] + ').'


			if f_isOK:

				# Definindo o id da thread para processar a solicitação
				bpeName = 'bern' + '{:03d}'.format(datetime.now().timetuple().tm_yday)
				bpeName += '_' +  '{:02d}'.format(datetime.now().timetuple().tm_hour)
				bpeName += '{:02d}'.format(datetime.now().timetuple().tm_min)
				bpeName += '{:02d}'.format(datetime.now().timetuple().tm_sec)

				headers = [b_header,r_header]
				pathTempFiles = [b_pathTempFile,r_pathTempFile]

				try:

					# Nova instancia da API para o Bernese
					rltBPE = ApiBernese(bpeName,headers,form.cleaned_data['email'],pathTempFiles)

					# Abrindo novo processo para a solicitação
					Thread(name=bpeName,target=rltBPE.runBPE,kwargs={'prcType': 'RLT'}).start()

					context['isOK'] = True  # retorno ao usuario de solicitação enviada com sucesso
					form = simpleRelative() # Novo formulário em branco

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

		form = simpleRelative() # Novo formulário em branco

	context['form'] = form

	return render(request, template_name, context)
