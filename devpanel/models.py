from django.db import models
from empresas.models import Empresa

# Create your models here.

class CustomAttribute(models.Model):
    """
    Define un atributo personalizado para un modelo específico de una empresa.
    """
    # --- Opciones predefinidas para los tipos de modelo y atributo ---
    MODEL_CHOICES = [
        ('Producto', 'Producto'),
        ('Servicio', 'Servicio'),
        # Aquí podrías añadir más modelos en el futuro, como 'Usuario'
    ]

    ATTRIBUTE_TYPE_CHOICES = [
        ('TEXT', 'Texto Corto'),
        ('TEXTAREA', 'Texto Largo'),
        ('NUMBER', 'Número'),
        ('DATE', 'Fecha'),
        ('BOOLEAN', 'Sí/No (Checkbox)'),
    ]

    # --- Campos del modelo ---

    # A qué empresa pertenece esta definición de atributo
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='custom_attributes')

    # A qué modelo base se aplica (Producto, Servicio, etc.)
    target_model = models.CharField(max_length=50, choices=MODEL_CHOICES)
    
    # El nombre del atributo (ej. "Talla", "Autor", "Material")
    name = models.CharField(max_length=100)

    # El tipo de dato que almacenará (Texto, Número, etc.)
    attribute_type = models.CharField(max_length=50, choices=ATTRIBUTE_TYPE_CHOICES)

    def __str__(self):
        # Esto ayuda a que se vea bien en el panel de admin de Django
        return f"{self.empresa.nombre} - {self.target_model}: {self.name} ({self.get_attribute_type_display()})"

    class Meta:
        # Evita que se pueda crear el mismo atributo dos veces para el mismo modelo y empresa
        unique_together = ('empresa', 'target_model', 'name')