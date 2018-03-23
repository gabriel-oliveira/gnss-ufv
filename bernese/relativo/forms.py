from django import forms

class simpleRelative(forms.Form):

	email = forms.EmailField(
		label = 'Email',
		max_length = 250,
		widget = forms.EmailInput(
			attrs = {'class': 'form-control'}
			)
		)

	rinexBaseFile = forms.FileField(
		label = 'Arquivo rinex da base',
		max_length = 250,
		widget = forms.ClearableFileInput(
			attrs = {'class': 'form-control'},
			)
		)

	rinexRoverFile = forms.FileField(
		label = 'Arquivo rinex do rover',
		max_length = 250,
		widget = forms.ClearableFileInput(
			attrs = {'class': 'form-control'},
			)
		)

	PLATE_CHOICES = (
		('SOAM', 'SOAM - Sul-Americana',),
		('AFRC', 'AFRC - Africa'),
		('ANTA', 'ANTA - Antarctica'),
		('ARAB', 'ARAB - Arabia'),
		('AUST', 'AUST - Australia'),
		('CARB', 'CARB - Caribbean'),
		('COCO', 'COCO - Cocos (north of NAZC, south of NOAM, east of CARB)'),
		('EURA', 'EURA - Eurasia'),
		('INDI', 'INDI - India'),
		('JUFU', 'JUFU - Juan de Fuca (in between northern NOAM and PCFC)'),
		('NAZC', 'NAZC - Nazca (west of SOAM, east of PCFC)'),
		('NOAM', 'NOAM - North America'),
		('SOAM', 'SOAM - South America'),
		('PCFC', 'PCFC - Pacific'),
		('PHIL', 'PHIL - Philippine'),
		)

	plateBase = forms.ChoiceField(
		label = 'Selecione a placa tectônica da estação Base:',
		choices = PLATE_CHOICES,
		initial = 'SOAM',
		required = True,
		widget=forms.Select(
			attrs={'class': 'form-control'},
			)
		)

	plateRover = forms.ChoiceField(
			label = 'Selecione a placa tectônica da estação Rover:',
			choices = PLATE_CHOICES,
			initial = 'SOAM',
			required = True,
			widget=forms.Select(
				attrs={'class': 'form-control'},
				)
		)

	blqFile = forms.FileField(
		label = 'Arquivo BLQ (Ocean Tide Loading)',
		max_length = 250,
		required = False,
		widget = forms.ClearableFileInput(
			attrs={'class': 'form-control'},

			)
		)

	choice_coord_from = forms.ChoiceField(
		label = 'Coordenadas de referência (BASE)',
		choices = (
			('COORD_FROM_RINEX', 'No cabeçalho do arquivo rinex',),
			('COORD_USER_DEFINED', 'Inserir manualmente',)
			),
		widget=forms.RadioSelect(
			attrs={'class': 'list-group'},
			)
		)

	coord_X = forms.DecimalField(
		label = ' X (m)',
		max_digits = 15,
		decimal_places = 6,
		disabled = True,
		required = False,
		widget = forms.NumberInput(
			attrs = {'class': 'form-control'}
			)
		)

	coord_Y = forms.DecimalField(
		label = 'Y (m)',
		max_digits = 15,
		decimal_places = 6,
		disabled = True,
		required = False,
		widget = forms.NumberInput(
			attrs = {'class': 'form-control'}
			)
		)

	coord_Z = forms.DecimalField(
		label = 'Z (m)',
		max_digits = 15,
		decimal_places = 6,
		disabled = True,
		required = False,
		widget = forms.NumberInput(
			attrs = {'class': 'form-control'}
			)
		)

	# TODO inserir época da coordenada para entrar no arquivo CRD
