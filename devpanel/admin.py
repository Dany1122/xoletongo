from django.contrib import admin
from .models import CustomAttribute, Pagina, Seccion, Rol

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

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'empresa', 'activo', 'total_usuarios', 'creado_en']
    list_filter = ['empresa', 'activo']
    search_fields = ['nombre', 'descripcion', 'empresa__nombre']
    ordering = ['empresa', 'nombre']
    
    def total_usuarios(self, obj):
        return obj.total_usuarios()
    total_usuarios.short_description = 'Usuarios'