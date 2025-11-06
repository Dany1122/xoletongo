from django.db import models
from empresas.models import Empresa


class ContactMessage(models.Model):
    """Modelo para almacenar mensajes de contacto"""
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='mensajes_contacto',
        help_text="Empresa a la que pertenece este mensaje"
    )
    
    # Campos dinámicos almacenados como JSON
    datos = models.JSONField(
        default=dict,
        help_text="Datos del formulario de contacto (nombre, email, mensaje, etc.)"
    )
    
    # Metadatos
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False, help_text="Marca si el mensaje fue leído")
    respondido = models.BooleanField(default=False, help_text="Marca si el mensaje fue respondido")
    notas_internas = models.TextField(blank=True, help_text="Notas internas del staff")
    
    # Info técnica
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Mensaje de Contacto'
        verbose_name_plural = 'Mensajes de Contacto'
        ordering = ['-fecha_envio']
    
    def __str__(self):
        nombre = self.datos.get('nombre', 'Sin nombre')
        return f"{nombre} - {self.fecha_envio.strftime('%d/%m/%Y %H:%M')}"
    
    def get_email(self):
        """Retorna el email del remitente"""
        return self.datos.get('email', 'Sin email')
    
    def get_asunto(self):
        """Retorna el asunto del mensaje"""
        return self.datos.get('asunto', 'Sin asunto')
    
    def get_mensaje(self):
        """Retorna el mensaje principal"""
        return self.datos.get('mensaje', 'Sin mensaje')
