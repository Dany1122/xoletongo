from django.db import models

# Create your models here.
class TipoServicio(models.Model):
    TIPO_SERVICIO_CHOICES = [
        ('hospedaje', 'Hospedaje'),
        ('visita', 'Visita'),
        ('restaurante', 'Restaurante'),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    tipo = models.CharField(max_length=50, choices=TIPO_SERVICIO_CHOICES)

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
    galeria = models.ManyToManyField('ImagenServicio', blank=True)

    def __str__(self):
        return self.titulo

class ImagenServicio(models.Model):
    imagen = models.ImageField(upload_to='servicios/galeria/')
    descripcion = models.CharField(max_length=150, blank=True)