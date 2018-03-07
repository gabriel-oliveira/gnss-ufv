from django import forms
from django.conf import settings

class ContactGeneral(forms.Form):

	name = forms.CharField(
		label = 'Nome',
		widget = forms.TextInput(attrs={'class': 'form-control'})
		)

	email = forms.EmailField(
		label='Email',
		widget = forms.EmailInput(
			attrs={'class': 'form-control'}
				)
		)

	message = forms.CharField(
		label = 'Mensagem/Sugestão',
		widget = forms.Textarea(attrs={'class': 'form-control'})
		)

class BerneseTools(forms.Form):


	widget_content = {'class': 'form-control',
					  'type' : 'date',
					  'placeholder' : '06/01/1980',
					  }

	date = forms.DateField(
							label = 'Data do rastreio',
							widget = forms.DateInput(attrs=widget_content)
						  )
