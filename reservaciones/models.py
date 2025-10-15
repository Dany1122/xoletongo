from django.db import models
from servicios.models import Servicio
from decimal import Decimal
from empresas.models import Empresa

# Create your models here.
class Reservacion(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('finalizada', 'Finalizada'),
    ]
    nombre_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField()
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    hora_recepcion = models.TimeField(null=True, blank=True)
    numero_adultos = models.PositiveIntegerField()
    numero_ninos = models.PositiveIntegerField()
    numero_descuento = models.PositiveIntegerField()
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(null=True, blank=True)
    pago_realizado = models.BooleanField(default=False)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    comprobante_pago = models.FileField(upload_to='comprobantes/', null=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default='pendiente'
    )
    def __str__(self):
        return f"Reserva de {self.nombre_cliente}"
    
    class Meta:
        verbose_name_plural='Reservaciones'

class Reservacion_servicio(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    id_reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE, related_name='reservacion')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='tipoServicio')

    def __str__(self):
        return f"Reserva de {self.id_reservacion} - {self.servicio}"
