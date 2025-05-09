from django.contrib import admin
from servicios.models import Servicio,ImagenServicio, TipoServicio
# Register your models here.
admin.site.register(Servicio)
admin.site.register(TipoServicio)
admin.site.register(ImagenServicio)