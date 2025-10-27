from django.contrib import admin
from servicios.models import Servicio, ImagenServicio, TipoServicio, Resena
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

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'calificacion', 'content_type', 'object_id', 'aprobada', 'fecha_creacion')
    list_filter = ('aprobada', 'calificacion', 'content_type', 'fecha_creacion')
    search_fields = ('usuario__username', 'comentario')
    readonly_fields = ('usuario', 'content_type', 'object_id', 'fecha_creacion', 'fecha_actualizacion')
    list_editable = ('aprobada',)
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        ('Información de la reseña', {
            'fields': ('usuario', 'calificacion', 'comentario', 'aprobada')
        }),
        ('Relación', {
            'fields': ('content_type', 'object_id')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )