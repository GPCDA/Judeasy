from django.contrib import admin

# Register your models here.

from .models import BaseDados

# Customizando o admin
class BaseAdmin(admin.ModelAdmin):

	list_display = ['name', 'slug']
	search_fields = ['name', 'slug']
	# prepopulated_fields = {'slug': ('name',)}

# Registrando o model da base de dados
admin.site.register(BaseDados, BaseAdmin)
