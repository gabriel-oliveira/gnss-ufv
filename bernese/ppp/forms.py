from django import forms
from django.forms import ModelForm
from bernese.ppp.models import Details_PPP
from bernese.core.utils import is_blq
from bernese.core.rinex import isRinex, readRinexObs
from zipfile import ZipFile, is_zipfile
from django.core.files.storage import default_storage

class simplePPP(ModelForm):

	def clean_rinex_file(self):
		rfile = self.cleaned_data['rinex_file']
		(r_isOK,erroMsg) = isRinex(rfile)

		# verifica se os arquivos compactados são validos
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
		rfile = cleaned_data.get('rinex_file')

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
		else:
			(f_isOK, erroMsg, header) = readRinexObs(rfile)

		if not f_isOK:
			 raise forms.ValidationError(erroMsg)


	def save(self, *args, **kwargs):

		rfile = self.cleaned_data['rinex_file']

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
						'tectonic_plate' : self.cleaned_data['tectonic_plate'],
						'blq_file' :  bfile_newname,
						'rinex_file' : rfile_name,
						'hoi_correction' : self.cleaned_data['hoi_correction'],
					}
					md = Details_PPP(**context)
					md.save()

		else:
			super().save(*args, **kwargs)


	# TODO: reescrever o save para o caso do zip
	#       from django.core.files.storage import default_storage
    #       default_storage.save('teste.txt',file_data['rinex_file'])
    #       retorna o nome do arquivo salvo 'teste_m0sd0PH.txt'
	#       nova instacia do models e loop para save model para cada arquivos
	#       else: super.save()


	class Meta:
		model = Details_PPP
		fields = ('email', 'rinex_file', 'tectonic_plate', 'blq_file','hoi_correction')
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
			'hoi_correction' : 'Correção dos efeitos ionosféricos de ordem superior',
		}
