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
