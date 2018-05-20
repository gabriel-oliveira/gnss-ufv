from django import forms
from bernese.relativo.models import Details_Relativo
from bernese.core.utils import is_blq
from bernese.core.rinex import isRinex, readRinexObs
from bernese.core.models import Coordinates
from datetime import date


class simpleRelativo(forms.ModelForm):

	# Verificando os dados contidos no campo rinex_base_file inserido no formulario
	def clean_rinex_base_file(self):
		rfile = self.cleaned_data['rinex_base_file']
		(r_isOK,erroMsg) = isRinex(rfile)
		if r_isOK:
			return rfile
		else:
			raise forms.ValidationError(erroMsg)

	# Verificando os dados contidos no campo rinex_rover_file inserido no formulario
	def clean_rinex_rover_file(self):
		rfile = self.cleaned_data['rinex_rover_file']
		(r_isOK,erroMsg) = isRinex(rfile)
		if r_isOK:
			return rfile
		else:
			raise forms.ValidationError(erroMsg)

	# Verificando os dados contidos no campo blq_file inserido no formulario
	def clean_blq_file(self):
		bfile = self.cleaned_data['blq_file']
		if bfile:
			(b_ok,erroMsg) = is_blq(bfile)
			if b_ok:
				return bfile
			else:
				raise forms.ValidationError(erroMsg)

	# Verificação final dos dados contidos no formulario
	#	Verifica se:
	#	- Se os dados são do mesmo dia_mes
	#	- Se os arquivos não são da mesma estação
	def clean(self):
		cleaned_data = super().clean()

		b_file = cleaned_data.get('rinex_base_file')
		r_file = cleaned_data.get('rinex_rover_file')

		if b_file and r_file:
			(b_isOK, b_erroMsg, b_header) = readRinexObs(b_file)
			(r_isOK, r_erroMsg, r_header) = readRinexObs(r_file)
		else:
			b_isOK = False
			b_isOK = False
			b_erroMsg = 'Arquivo rinex invalido.'
			r_erroMsg = ''

		if not b_isOK or not r_isOK:
			 raise forms.ValidationError(b_erroMsg + r_erroMsg)


		# # Verificando se os dois arquivos são do mesmo dia

		b_Date = b_header['TIME OF FIRST OBS'].split()
		b_day = date(year=int(b_Date[0]),month=int(b_Date[1]),day=int(b_Date[2]))
		r_Date = r_header['TIME OF FIRST OBS'].split()
		r_day = date(year=int(r_Date[0]),month=int(r_Date[1]),day=int(r_Date[2]))

		if b_day != r_day:
			erroMsg = 'As observações não são do mesmo dia.'
			raise forms.ValidationError(erroMsg)


		# # Verificando o nome das estações

		for header in [r_header, b_header]:
			if not r_header['MARKER NAME']:
				erroMsg = 'Favor definir o nome da estação do arquivo '
				erroMsg += r_header['RAW_NAME']
				raise forms.ValidationError(erroMsg)

		if r_header['MARKER NAME'] == b_header['MARKER NAME']:
			erroMsg = 'Arquivos da mesma estação (' + b_header['MARKER NAME'] + ').'
			raise forms.ValidationError(erroMsg)


		# # Verificando as coordenadas de referencia

		if self.cleaned_data['coord_ref_type'] == 'header_rinex':
			self.cleaned_data['coord_X'] = float(b_header['APPROX POSITION XYZ'][0])
			self.cleaned_data['coord_Y'] = float(b_header['APPROX POSITION XYZ'][1])
			self.cleaned_data['coord_Z'] = float(b_header['APPROX POSITION XYZ'][2])

		if (not self.cleaned_data['coord_X'] or not self.cleaned_data['coord_Y']
		 	or not self.cleaned_data['coord_Z']):
			 raise forms.ValidationError(
			 	'Favor definir as coordenadas de referência')


	# Cria e persiste nova instancia das coordenadas de referenica da estação base
	def save_coord_form(self):

		coord_context = {
			'datum' : self.cleaned_data['datum'],
			'epoch' : float(self.cleaned_data['epoch']),
			'devX' : 0.0,
			'devY' : 0.0,
			'devZ' : 0.0,
		}

		# Leitura do arq rinex
		rFile = self.cleaned_data['rinex_base_file'].open('rb')
		(is_ok, erroMsg, header) = readRinexObs(rFile)
		if not is_ok:
			raise forms.ValidationError(
				'Erro ao persistir a coordenada de referencia. ' +
				'Erro ao ler o arquivo rinex! ' + erroMsg
			) # TODO usar outra exception

		# Atribuindo nome da estação
		coord_context['station_name'] = header['MARKER NAME']

		# Leitura das coordenadas no cabecalho do arquivo rinex ou do formulário
		# conforme especificado pelo usuário
		coord_context['X'] = self.cleaned_data['coord_X']
		coord_context['Y'] = self.cleaned_data['coord_Y']
		coord_context['Z'] = self.cleaned_data['coord_Z']

		if self.cleaned_data['coord_ref_type'] not in ['header_rinex','user_set']:
			raise forms.ValidationError('Favor definir a origem da coordenada' +
			 							' de referência.') # TODO usar outra exception


		# Criando uma instancia da Classe coordenadas com os atributos do coord_context
		coord_ref = Coordinates(**coord_context)

		# Persistindo coordenadas no bando de dados
		coord_ref.save()

		#fim com sucesso da função save_coord_form
		return coord_ref       # Retornando uma instancia da classe coordenadas



	# Fução save() do ModelForm reescrita para salvar as coordenadas de referencia
	# antes da solicitação de processamento ser persistida no BD.
	def save(self, *args, **kwargs):
		r_model = super().save(commit = False, *args, **kwargs)
		r_model.coord_ref = self.save_coord_form()
		r_model.save()

	# TODO: Tranformar em ForeignKey para reference systems do postgis
	datum = forms.ChoiceField(
		label = 'Sistema de Referência',
		required = True,
		choices = (
			('SIRGAS2000', 'SIRGAS 2000'),
			('ITRF14', 'ITRF 2014'),
			('ITRF08', 'ITRF 2008'),
			('ITRF05', 'ITRF 2005'),
			('ITRF00', 'ITRF 2000'),
			('WGS84', 'WGS84'),
		),
		initial = 'SIRGAS2000',
		widget=forms.Select(
			attrs={'class': 'form-control'},
			)
	)

	epoch = forms.FloatField(
		label = 'Época da Coordenada',
		required = True,
		initial = 2000.4,
		widget=forms.NumberInput(
			attrs={'class': 'form-control'},
			)
	)

	coord_X = forms.DecimalField(
		label = ' X (m)',
		max_digits = 15,
		decimal_places = 6,
		required = False,
		widget = forms.NumberInput(
			attrs = {'class': 'form-control'}
			)
		)

	coord_Y = forms.DecimalField(
		label = 'Y (m)',
		max_digits = 15,
		decimal_places = 6,
		required = False,
		widget = forms.NumberInput(
			attrs = {'class': 'form-control'}
			)
		)

	coord_Z = forms.DecimalField(
		label = 'Z (m)',
		max_digits = 15,
		decimal_places = 6,
		required = False,
		widget = forms.NumberInput(
			attrs = {'class': 'form-control'}
			)
		)

	class Meta:
		model = Details_Relativo
		fields = (
			'email', 'rinex_base_file', 'rinex_rover_file',
			'tectonic_plate_base', 'tectonic_plate_rover', 'blq_file',
			'coord_ref_type', #'coord_ref'
			)
		widgets = {
			'email': forms.EmailInput(attrs={'class': 'form-control'}),
			'rinex_base_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
			'rinex_rover_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
			'tectonic_plate_base': forms.Select(attrs={'class': 'form-control'}),
			'tectonic_plate_rover': forms.Select(attrs={'class': 'form-control'}),
			'blq_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
			'coord_ref_type' : forms.RadioSelect(attrs={'class': 'list-group'}),

		}
		labels = {
			'email' : 'E-mail',
			'rinex_base_file' : 'Arquivo Rinex de Observação da BASE',
			'rinex_rover_file' : 'Arquivo Rinex de Observação do ROVER',
			'tectonic_plate_base' : 'Selecione a placa tectônica da estação BASE',
			'tectonic_plate_rover' : 'Selecione a placa tectônica da estação ROVER',
			'blq_file' : 'Arquivo BLQ (Ocean Tide Loading)',
			'coord_ref_type' : 'Coordenadas de referência (BASE)'
		}
