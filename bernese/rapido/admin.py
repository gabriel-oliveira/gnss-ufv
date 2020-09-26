from django.contrib import admin
from .models import Details_Rapido
from django.utils.html import format_html

class Details_Rapido_Admin(admin.ModelAdmin):

	exclude = ['proc_method']

	list_display = ['id', 'proc_status', 'created_at', 'started_at',
					'finished_at', 'blq_file', 'rinex_base_file',
					'rinex_rover_file', 'coord_ref_type', 'link_coord_ref']

	def link_coord_ref(self, obj):

		if obj.coord_ref:

			id = obj.coord_ref.id

			return format_html(
				'<a href="/admin/core/coordinates/{}/change">{}</a>',
				id,
				id,
			)

		else:
			return None

	link_coord_ref.short_description = 'Coordenada de Referência'


admin.site.register(Details_Rapido, Details_Rapido_Admin)
