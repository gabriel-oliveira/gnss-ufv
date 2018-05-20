from django.contrib import admin
from .models import Details_PPP

class Details_PPP_Admin(admin.ModelAdmin):

	exclude = ['proc_method']
	list_display = ['id', 'proc_status', 'created_at', 'started_at','finished_at', 'blq_file', 'rinex_file']
	# search_fields = ['', '']
	# prepopulated_fields = {'': ('',)}

admin.site.register(Details_PPP, Details_PPP_Admin)
