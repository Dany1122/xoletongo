from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    nombre_completo = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.username
