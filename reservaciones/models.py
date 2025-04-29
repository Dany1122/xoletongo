from django.db import models
from servicios.models import Servicio

# Create your models here.
class Reservacion(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    numero_personas = models.PositiveIntegerField()
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(null=True, blank=True)  # Comentarios adicionales del cliente
    pago_realizado = models.BooleanField(default=False)

    def __str__(self):
        return f"Reserva de {self.nombre_cliente}"
    
class Reservacion_servicio(models.Model):
    id_reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE, related_name='reservacion')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='tipoServicio')