from django.contrib import admin
from reservaciones.models import Reservacion, Reservacion_servicio

# Register your models here.
admin.site.register(Reservacion)
admin.site.register(Reservacion_servicio)