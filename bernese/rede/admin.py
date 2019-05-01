from django.contrib import admin
from .models import Details_Rede
from django.utils.html import format_html

class Details_Rede_Admin(admin.ModelAdmin):

	exclude = ['proc_method']

	list_display = ['id', 'proc_status', 'created_at', 'started_at',
					'finished_at', 'blq_file', 'rinex_rover_file',
                    'base_select_max_distance']


admin.site.register(Details_Rede, Details_Rede_Admin)
