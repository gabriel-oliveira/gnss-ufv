from django import forms
from bernese.rede.models import Details_Rede, get_basesRBMC
from bernese.core.models import basesRBMC
from bernese.core.utils import is_blq
from bernese.core.rinex import isRinex, readRinexObs
from zipfile import ZipFile, is_zipfile
from django.core.files.storage import default_storage


class redeRelativo(forms.ModelForm):

	# Verificando os dados contidos no campo rinex_rover_file inserido no formulario
	def clean_rinex_rover_file(self):
		rfile = self.cleaned_data['rinex_rover_file']
		(r_isOK,erroMsg) = isRinex(rfile)

		if is_zipfile(rfile):
			with ZipFile(rfile) as zfile:
				for file in zfile.namelist():
					with zfile.open(file) as rzfile:
						(r_isOK,erroMsg) = isRinex(rzfile)
					if not r_isOK: raise forms.ValidationError(erroMsg)

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

	def clean(self):
		cleaned_data = super().clean()

		rfile = cleaned_data.get('rinex_rover_file')

		headers= []

		if not rfile:
			f_isOK = False
			erroMsg = 'Arquivo invalido.'
		elif is_zipfile(rfile):
			# verifica se os arquivos compactados são validos
			with ZipFile(rfile) as zfile:
				for file in zfile.namelist():
					with zfile.open(file) as rzfile:
						(f_isOK, erroMsg, header) = readRinexObs(rzfile)
					if not f_isOK: raise forms.ValidationError(erroMsg)
					else: headers.append(header)
		else:
			(f_isOK, erroMsg, header) = readRinexObs(rfile)
			headers = [header]

		if not f_isOK:
			 raise forms.ValidationError(erroMsg)

		for header in headers:
			# # Verificando o nome das estações
			if not header['MARKER NAME']:
				erroMsg = 'Favor definir o nome da estação do arquivo '
				erroMsg += header['RAW_NAME']
				raise forms.ValidationError(erroMsg)

			# # Verificando as coordenadas aproximadas
			coord_X = 0
			coord_Y = 0
			coord_Z = 0
			if self.cleaned_data['coord_ref_type'] == 'header_rinex':
				coord_X = float(header['APPROX POSITION XYZ'][0])
				coord_Y = float(header['APPROX POSITION XYZ'][1])
				coord_Z = float(header['APPROX POSITION XYZ'][2])

			if (not coord_X or not coord_Y or not coord_Z):
				 raise forms.ValidationError(
				 	'Favor definir as coordenadas aproximadas da estação no arquivo ' + header['RAW_NAME'])

			# Pré-seleção das bases da RBMC (Validação da existencia do arquivo na API do Bernese)
			bases_names = ''
			self.bases = {}
			
			if self.cleaned_data['base_select_type'] == 'auto':
				bases = basesRBMC(coord_X,coord_Y,coord_Z,cleaned_data['base_select_max_distance'])
			elif self.cleaned_data['base_select_type'] == 'manual':
				bases = cleaned_data['bases_rbmc_choices'].replace(" ","").replace("'","").replace('[','').replace(']','').split(',') 
			
			for base in bases:
				if base != header['MARKER NAME']:
					bases_names += base
					bases_names += ' '

			if bases_names:
				self.bases[header['RAW_NAME']] = bases_names
			else:
				raise forms.ValidationError(
				'Não foram encontradas bases da RBMC para o arquivo ' + header['RAW_NAME'] +
				' em um raio de {}km'.format(cleaned_data['base_select_max_distance']))


	def save(self, *args, **kwargs):

		rfile = self.cleaned_data['rinex_rover_file']

		if is_zipfile(rfile):

			bfile = self.cleaned_data['blq_file']
			if bfile:
				bfile_newname = default_storage.save(bfile.name,bfile)
			else:
				bfile_newname = ''

			# uma nova instancia de solicitação de processamento para cada arquivo compactado
			with ZipFile(rfile) as zfile:
				for file in zfile.namelist():
					with zfile.open(file) as rzfile:
						rfile_name = default_storage.save(rzfile.name,rzfile)
					context = {
						'email' : self.cleaned_data['email'],
						'tectonic_plate_rover' : self.cleaned_data['tectonic_plate_rover'],
						'tectonic_plate_base' : self.cleaned_data['tectonic_plate_base'],
						'blq_file' :  bfile_newname,
						'rinex_rover_file' : rfile_name,
						'hoi_correction' : self.cleaned_data['hoi_correction'],
						'base_select_type' :  self.cleaned_data['base_select_type'],
						'base_select_max_distance' :  self.cleaned_data['base_select_max_distance'],
						'coord_ref_type' :  self.cleaned_data['coord_ref_type'],
						'bases_rbmc' : self.bases[file],
					}
					md = Details_Rede(**context)
					md.save()

		else:
			f = super().save(*args, **kwargs, commit=False)
			f.bases_rbmc = self.bases[rfile.name]
			f.save()



	datum = forms.ChoiceField(
		label = 'Sistema de Referência',
		required = True,
		choices = (
			('ITRF2014', 'ITRF2014'),
			('ITRF2008', 'ITRF2008'),
			('ITRF2005', 'ITRF2005'),
			('ITRF2000', 'ITRF2000'),
			('SIRGAS2000', 'SIRGAS2000'),
			('IGS14', 'IGS14'),
			('IGS08', 'IGS08'),
			('IGb08', 'IGb08'),
			('IGS05', 'IGS05'),
			('IGS_00', 'IGS00'),
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
		model = Details_Rede
		fields = (
			'email', 'rinex_rover_file', 'base_select_type', 'base_select_max_distance', 
			'bases_rbmc_choices', 'tectonic_plate_base', 'tectonic_plate_rover',
			'blq_file', 'hoi_correction', 'coord_ref_type', #'coord_ref'
			)
		widgets = {
			'email': forms.EmailInput(attrs={'class': 'form-control'}),
			'rinex_rover_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
			'base_select_type': forms.RadioSelect(attrs={'class': 'list-group'}),
			'base_select_max_distance' : forms.NumberInput(attrs={'class': 'form-control'}),
			'bases_rbmc_choices': forms.SelectMultiple(attrs={
				'class': 'form-control chosen-select-no-results',
				'data-placeholder': 'Buscar Estação'},
				choices=get_basesRBMC(),
				),
			'tectonic_plate_base': forms.Select(attrs={'class': 'form-control'}),
			'tectonic_plate_rover': forms.Select(attrs={'class': 'form-control'}),
			'blq_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
			'coord_ref_type' : forms.RadioSelect(attrs={'class': 'list-group'}),

		}
		labels = {
			'email' : 'E-mail',
			'rinex_rover_file' : 'Arquivo Rinex de Observação do ROVER',
			'base_select_type': 'Seleção das estações de referência (BASE)',
			'base_select_max_distance' : 'Raio máximo de distância para seleção das BASES (KM)',
			'bases_rbmc_choices': 'Selecione as estações de referência da RBMC',
			'tectonic_plate_base' : 'Selecione a placa tectônica das estações BASE',
			'tectonic_plate_rover' : 'Selecione a placa tectônica das estações ROVER',
			'blq_file' : 'Arquivo BLQ (Ocean Tide Loading)',
			'coord_ref_type' : 'Coordenadas de referência (BASE)',
			'hoi_correction' : 'Correção dos efeitos ionosféricos de ordem superior',
		}
