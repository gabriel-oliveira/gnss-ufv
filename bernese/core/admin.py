from django.contrib import admin
from .models import Proc_Request, Coordinates
from django.utils.html import format_html
from django_celery_results.models import TaskResult

class Proc_Request_Admin(admin.ModelAdmin):

	readonly_fields = ('proc_method','task_id','started_at','finished_at')
	list_display = [
		'id', 'proc_method', 'proc_status', 'created_at', 'details', 'task'
	]

	def task(self, obj):

		if obj.task_id:
			task = TaskResult.objects.get(task_id=obj.task_id)

			context = {
				'id' : task.id,
				'status': task.status,
			}

			return format_html(
				'<a href="/controle/django_celery_results/taskresult/{id}/change">{status}</a>',
				**context,
			)

	def details(self, obj):

		context = {
			'method' : obj.proc_method,
			'id' : obj.id,
		}

		return format_html(
			'<a href="/controle/{method}/details_{method}/{id}/change">{method}_{id}</a>',
			**context,
		)


class Coordinates_Admin(admin.ModelAdmin):
	list_display = [
		'id', 'station_name', 'X', 'Y', 'Z', 'epoch', 'datum', 'devX', 'devY', 'devZ'
	]
	# list_display_link = ['station_name']

admin.site.register(Proc_Request, Proc_Request_Admin)
admin.site.register(Coordinates, Coordinates_Admin)
