from django.db import models
from empresas.models import Empresa

# Create your models here.
def upload_to_service_gallery(instance, filename):
    # Guarda las imágenes en: servicios/<id_servicio>/galeria/<archivo>
    servicio_id = instance.servicio_id or 'sin-id'
    return f"servicios/{servicio_id}/galeria/{filename}"

class TipoServicio(models.Model):
    TIPOS = [
        ('porDia', 'Por día'),
        ('porHora', 'Por hora'),
    ]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    tipo = models.CharField(max_length=15, choices=TIPOS)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    titulo = models.CharField(max_length=200)
    servicio = models.ForeignKey(TipoServicio, on_delete=models.CASCADE, related_name='subservicios')
    descripcion = models.TextField()
    costo_por_persona = models.DecimalField(max_digits=6, decimal_places=2)
    costo_niño = models.DecimalField(max_digits=6, decimal_places=2)
    costo_con_descuento = models.DecimalField(max_digits=6, decimal_places=2)
    imagen_principal = models.ImageField(upload_to='servicios/')
    duracion = models.PositiveIntegerField(null=True, blank=True)
    restricciones = models.TextField(null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return self.titulo

class ImagenServicio(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to=upload_to_service_gallery)
    descripcion = models.CharField(max_length=150, blank=True)
    orden = models.PositiveIntegerField(default=0,blank=True, help_text="Orden en la galería (0 arriba).")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    class Meta:
        ordering = ['orden', 'id']

    def __str__(self):
        return self.descripcion or f"Imagen de {self.servicio.titulo} #{self.pk}"