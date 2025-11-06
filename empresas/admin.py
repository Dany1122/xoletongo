from django.contrib import admin
from .models import Empresa, Tema

# Register your models here.

@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estilo_layout', 'activo', 'creado_en']
    list_filter = ['activo', 'estilo_layout']
    search_fields = ['nombre']
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'estilo_layout', 'activo')
        }),
        ('Colores', {
            'fields': ('color_primario', 'color_secundario', 'color_acento', 'color_texto', 'color_fondo')
        }),
        ('Tipografía', {
            'fields': ('fuente_principal', 'fuente_secundaria')
        }),
        ('Imágenes', {
            'fields': ('logo_header', 'imagen_hero', 'favicon')
        }),
    )

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tema', 'subdominio', 'activa', 'fecha_creacion']
    list_filter = ['activa', 'tema']
    search_fields = ['nombre', 'subdominio', 'dominio_personalizado']
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'nombre_titular', 'correo_contacto', 'telefono', 'ubicacion')
        }),
        ('Branding', {
            'fields': ('logotipo', 'tema')
        }),
        ('Multi-sitio', {
            'fields': ('subdominio', 'dominio_personalizado', 'sitio_web', 'activa')
        }),
        ('Información Bancaria', {
            'fields': ('cuenta_bancaria', 'clabe', 'numero_terjeta'),
            'classes': ('collapse',)
        }),
        ('Configuración SMTP', {
            'fields': ('smtp_host', 'smtp_port', 'smtp_user', 'smtp_password', 'smtp_use_tls', 'smtp_use_ssl'),
            'classes': ('collapse',)
        }),
    )
