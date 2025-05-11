from django.db import models

# Create your models here.
class Empresa(models.Model):
    nombre = models.CharField(max_length=100)
    correo_contacto = models.EmailField()
    telefono = models.CharField(max_length=20)
    ubicacion = models.CharField(max_length=255)
    cuenta_bancaria = models.CharField(max_length=100)
    clabe = models.CharField(max_length=18)
    logotipo = models.ImageField(upload_to='empresas/logos/', null=True, blank=True)
    sitio_web = models.URLField(blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Empresas"

    def __str__(self):
        return self.nombre