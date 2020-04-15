from django.contrib import admin

# Register your models here.
from herramienta.models import Tema, Categoria, Tweet

admin.site.register(Tema)
admin.site.register(Categoria)
admin.site.register(Tweet)