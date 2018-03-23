from django import forms

class simplePPP(forms.Form):

	email = forms.EmailField(
		label = 'Email',
		max_length = 250,
		widget = forms.EmailInput(
			attrs={'class': 'form-control'}
			)
		)

	rinexFile = forms.FileField(
		label = 'Arquivo Rinex',
		max_length = 250,
		widget = forms.ClearableFileInput(
			attrs={'class': 'form-control'},

			)
		)

	# true_false_choices = (
	# 	(True, 'Sim',),
	# 	(False, 'Não',),
	# 	)
	#
	# blqCheck = forms.BooleanField(
	# 	label = 'Estação da RBMC',
	# 	required = False,
	# 	initial = False,
	# 	widget = forms.RadioSelect(
	# 		choices = true_false_choices
	# 		)
	# 	)

	plate = forms.ChoiceField(
		label = 'Selecione a placa tectônica da estação:',
		choices = (
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
			),
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
