from django.shortcuts import render

def index(request):
	template_name = 'ppp/index.html'
	context = {}
	context['isPPP'] = True
	return render(request, template_name, context)
