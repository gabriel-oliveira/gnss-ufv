from django.contrib import admin
from .models import Proc_Request, Coordinates
from django.utils.html import format_html

class Proc_Request_Admin(admin.ModelAdmin):

	exclude = ['proc_method']

	list_display = [
		'id', 'proc_method', 'proc_status', 'created_at', 'started_at',
		'finished_at', 'details',
	]

	def details(self, obj):

		context = {
			'method' : obj.proc_method,
			'id' : obj.id,
		}

		return format_html(
			'<a href="/admin/{method}/details_{method}/{id}/change">{method}_{id}</a>',
			**context,
		)


class Coordinates_Admin(admin.ModelAdmin):
	list_display = [
		'id', 'station_name', 'X', 'Y', 'Z', 'epoch', 'datum', 'devX', 'devY', 'devZ'
	]
	# list_display_link = ['station_name']

admin.site.register(Proc_Request, Proc_Request_Admin)
admin.site.register(Coordinates, Coordinates_Admin)
