from django.contrib import admin
from .models import CustomAttribute, Pagina, Seccion

# Register your models here.
admin.site.register(CustomAttribute)

@admin.register(Pagina)
class PaginaAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'slug', 'titulo', 'activa', 'actualizado_en']
    list_filter = ['empresa', 'slug', 'activa']
    search_fields = ['titulo', 'empresa__nombre']

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ['pagina', 'tipo', 'titulo', 'orden', 'activa', 'actualizado_en']
    list_filter = ['pagina__empresa', 'tipo', 'activa']
    search_fields = ['titulo', 'pagina__titulo']
    ordering = ['pagina', 'orden']