from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from empresas.models import Empresa

User = get_user_model()

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
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

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
    atributos_personalizados = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.titulo

class ImagenServicio(models.Model):
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to=upload_to_service_gallery)
    descripcion = models.CharField(max_length=150, blank=True)
    orden = models.PositiveIntegerField(default=0,blank=True, help_text="Orden en la galería (0 arriba).")

    @property
    def empresa(self):
        """Obtiene la empresa a través del servicio (evita FK redundante)"""
        return self.servicio.empresa

    class Meta:
        ordering = ['orden', 'id']

    def __str__(self):
        return self.descripcion or f"Imagen de {self.servicio.titulo} #{self.pk}"


class Resena(models.Model):
    """
    Modelo de reseñas que funciona para Servicios y Productos usando ContentTypes
    """
    # Usuario que hace la reseña
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resenas')
    
    # Relación genérica con Servicio o Producto
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Contenido de la reseña
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de 1 a 5 estrellas"
    )
    comentario = models.TextField(help_text="Comentario de la reseña")
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    aprobada = models.BooleanField(default=True, help_text="Si está aprobada por el administrador")
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        # Un usuario solo puede hacer una reseña por servicio/producto
        unique_together = ['usuario', 'content_type', 'object_id']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"Reseña de {self.usuario.username} - {self.calificacion} estrellas"
    
    @property
    def estrellas_llenas(self):
        """Retorna el número de estrellas llenas"""
        return range(self.calificacion)
    
    @property
    def estrellas_vacias(self):
        """Retorna el número de estrellas vacías"""
        return range(5 - self.calificacion)