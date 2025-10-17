from django.db import models

# Create your models here.
class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    nombre_titular = models.CharField(max_length=100)
    correo_contacto = models.EmailField()
    telefono = models.CharField(max_length=20)
    ubicacion = models.CharField(max_length=255)
    cuenta_bancaria = models.CharField(max_length=18)
    clabe = models.CharField(max_length=18)
    numero_terjeta = models.CharField(max_length=16)
    logotipo = models.ImageField(upload_to='empresas/logos/', null=True, blank=True)
    sitio_web = models.URLField(blank=True, null=True)
    activa = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    smtp_host = models.CharField(max_length=150, blank=True, null=True, help_text="Servidor SMTP (p. ej. smtp.gmail.com)")
    smtp_port = models.PositiveIntegerField(default=587, help_text="Puerto SMTP (p. ej. 587 para TLS, 465 para SSL)")
    smtp_user = models.CharField(max_length=100, blank=True, null=True, help_text="Usuario SMTP (p. ej. nombre@dominio.com)")
    smtp_password = models.CharField(max_length=100, blank=True, null=True, help_text="Contraseña SMTP (o contraseña de aplicación)")
    smtp_use_tls = models.BooleanField(default=True, help_text="Activar TLS al enviar correo")
    smtp_use_ssl = models.BooleanField(default=False, help_text="Activar SSL al enviar correo")
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.nombre