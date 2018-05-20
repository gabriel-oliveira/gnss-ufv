from django import forms
from django.forms import ModelForm
from bernese.ppp.models import Details_PPP
from bernese.core.utils import is_blq
from bernese.core.rinex import isRinex, readRinexObs

class simplePPP(ModelForm):

	def clean_rinex_file(self):
		rfile = self.cleaned_data['rinex_file']
		(r_isOK,erroMsg) = isRinex(rfile)
		if r_isOK:
			return rfile
		else:
			raise forms.ValidationError(erroMsg)

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

		f = cleaned_data.get('rinex_file')
		if f:
			(f_isOK, erroMsg, header) = readRinexObs(f)
		else:
			f_isOK = False
			erroMsg = 'Arquivo Rinex invalido.'

		if not f_isOK:
			 raise forms.ValidationError(erroMsg)


	class Meta:
		model = Details_PPP
		fields = ('email', 'rinex_file', 'tectonic_plate', 'blq_file')
		widgets = {
			'email': forms.EmailInput(attrs={'class': 'form-control'}),
			'rinex_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
			'tectonic_plate': forms.Select(attrs={'class': 'form-control'}),
			'blq_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
		}
		labels = {
			'email' : 'E-mail',
			'rinex_file' : 'Arquivo Rinex de Observação',
			'tectonic_plate' : 'Selecione a placa tectônica da estação',
			'blq_file' : 'Arquivo BLQ (Ocean Tide Loading)',
		}
