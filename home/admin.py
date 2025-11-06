from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_display', 'get_email_display', 'get_asunto_display', 'empresa', 'fecha_envio', 'leido', 'respondido')
    list_filter = ('leido', 'respondido', 'fecha_envio', 'empresa')
    search_fields = ('datos__nombre', 'datos__email', 'datos__asunto', 'datos__mensaje')
    readonly_fields = ('empresa', 'display_datos', 'fecha_envio', 'ip_address', 'user_agent')
    list_editable = ('leido', 'respondido')
    ordering = ('-fecha_envio',)
    
    fieldsets = (
        ('Información del mensaje', {
            'fields': ('empresa', 'display_datos', 'leido', 'respondido')
        }),
        ('Notas internas', {
            'fields': ('notas_internas',)
        }),
        ('Metadatos técnicos', {
            'fields': ('fecha_envio', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def get_nombre_display(self, obj):
        return obj.datos.get('nombre', 'Sin nombre')
    get_nombre_display.short_description = 'Nombre'
    
    def get_email_display(self, obj):
        email = obj.datos.get('email', 'Sin email')
        return format_html('<a href="mailto:{}">{}</a>', email, email)
    get_email_display.short_description = 'Email'
    
    def get_asunto_display(self, obj):
        return obj.datos.get('asunto', 'Sin asunto')
    get_asunto_display.short_description = 'Asunto'
    
    def display_datos(self, obj):
        """Muestra todos los datos del formulario de forma legible"""
        html = '<table style="width: 100%; border-collapse: collapse;">'
        for key, value in obj.datos.items():
            html += f'<tr style="border-bottom: 1px solid #ddd;">'
            html += f'<td style="padding: 8px; font-weight: bold; width: 30%;">{key.title()}:</td>'
            html += f'<td style="padding: 8px;">{value}</td>'
            html += f'</tr>'
        html += '</table>'
        return format_html(html)
    display_datos.short_description = 'Datos del formulario'
    
    def has_add_permission(self, request):
        # No permitir agregar mensajes desde el admin
        return False
