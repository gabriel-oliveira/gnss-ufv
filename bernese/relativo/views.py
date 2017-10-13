from django.shortcuts import render

def index(request):
	template_name = 'relativo/index.html'
	context = {}
	context['isRelativo'] = True
	return render(request, template_name, context)
