from django.contrib import admin
from servicios.models import Servicio,ImagenServicio, TipoServicio
# Register your models here.
class ImagenServicioInline(admin.TabularInline):
    model = ImagenServicio
    extra = 1
    fields = ('imagen', 'descripcion', 'orden')
    ordering = ('orden',)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'servicio', 'empresa')
    list_filter = ('servicio', 'empresa')
    search_fields = ('titulo', 'descripcion')
    inlines = [ImagenServicioInline]

@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo')
    search_fields = ('nombre',)

@admin.register(ImagenServicio)
class ImagenServicioAdmin(admin.ModelAdmin):
    list_display = ('servicio', 'descripcion', 'orden')
    list_filter = ('servicio',)
    ordering = ('servicio', 'orden')