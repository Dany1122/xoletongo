from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    nombre_completo = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    empresa = models.ForeignKey('empresas.Empresa', on_delete=models.CASCADE, null=True, blank=True)

    # DEPRECADO: Mantener por compatibilidad durante migración
    ROLES = (
        ('Administrador', 'Administrador'),
        ('Empleado', 'Empleado'),
        ('Encargado', 'Encargado'),
        ('Cliente', 'Cliente'),
    )
    rol_legacy = models.CharField(
        max_length=20, 
        choices=ROLES, 
        default='Cliente',
        null=True,
        blank=True,
        db_column='rol',
        help_text="DEPRECADO: usar campo 'rol' en su lugar"
    )
    
    # Nuevo sistema de roles dinámicos
    rol = models.ForeignKey(
        'devpanel.Rol',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        help_text="Rol del usuario con atributos personalizados",
        db_column='rol_id'
    )
    
    # Valores de los atributos personalizados definidos en el rol
    # Formato: {"Turno": "Matutino", "Idiomas": "Español, Inglés", ...}
    atributos_personalizados = models.JSONField(
        default=dict,
        blank=True,
        help_text="Valores de los atributos personalizados según el rol asignado"
    )

    def __str__(self):
        return self.username
    
    def get_rol_nombre(self):
        """Retorna el nombre del rol actual (compatible con ambos sistemas)"""
        if self.rol:
            return self.rol.nombre
        return self.rol_legacy if self.rol_legacy else 'Sin Rol'
