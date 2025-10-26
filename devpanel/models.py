from django.db import models
from empresas.models import Empresa

# Create your models here.

class Pagina(models.Model):
    """
    Representa una página del sitio web (Home, Servicios, Productos, etc.)
    """
    PAGINA_CHOICES = [
        ('home', 'Inicio'),
        ('servicios', 'Servicios'),
        ('productos', 'Productos'),
        ('nosotros', 'Nosotros'),
        ('galeria', 'Galería'),
        ('contacto', 'Contacto'),
        ('footer', 'Footer'),
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='paginas')
    slug = models.CharField(max_length=50, choices=PAGINA_CHOICES)
    titulo = models.CharField(max_length=200)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('empresa', 'slug')
        ordering = ['slug']
        verbose_name = 'Página'
        verbose_name_plural = 'Páginas'
    
    def __str__(self):
        return f"{self.empresa.nombre} - {self.get_slug_display()}"


class Seccion(models.Model):
    """
    Representa una sección dentro de una página (Hero, Carousel, Texto, etc.)
    """
    TIPO_CHOICES = [
        ('hero', 'Hero (Banner Principal)'),
        ('texto', 'Bloque de Texto'),
        ('carousel', 'Carrusel de Imágenes'),
        ('galeria', 'Galería de Imágenes'),
        ('features', 'Características/Beneficios'),
        ('cta', 'Call to Action'),
        ('testimonios', 'Testimonios'),
        ('mapa', 'Mapa'),
        ('instagram', 'Instagram Feed'),
        ('contacto_form', 'Formulario de Contacto'),
        ('servicios_accordion', 'Tarjetas de Servicios'),
    ]
    
    pagina = models.ForeignKey(Pagina, on_delete=models.CASCADE, related_name='secciones')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200, blank=True, help_text="Título interno para identificar la sección")
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición (menor número = más arriba)")
    activa = models.BooleanField(default=True)
    
    # JSONField para guardar toda la configuración específica de cada tipo de sección
    configuracion = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Configuración específica de la sección (título, subtítulo, imágenes, etc.)"
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['orden', 'creado_en']
        verbose_name = 'Sección'
        verbose_name_plural = 'Secciones'
    
    def __str__(self):
        titulo_display = self.titulo or self.get_tipo_display()
        return f"{self.pagina.slug} - {titulo_display} (Orden: {self.orden})"


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


class Rol(models.Model):
    """
    Modelo para roles de usuario dinámicos.
    Cada empresa puede crear sus propios roles con atributos personalizados.
    """
    nombre = models.CharField(max_length=100, help_text="Nombre del rol (ej: Guía Turístico)")
    descripcion = models.TextField(blank=True, help_text="Descripción de las responsabilidades del rol")
    empresa = models.ForeignKey(
        'empresas.Empresa', 
        on_delete=models.CASCADE, 
        related_name='roles',
        help_text="Empresa a la que pertenece este rol"
    )
    
    # Esquema de atributos personalizados que tendrán los usuarios con este rol
    # Formato: [{"nombre": "Turno", "tipo": "lista", "opciones": ["Matutino", "Vespertino"], "requerido": true}, ...]
    atributos_schema = models.JSONField(
        default=list, 
        blank=True,
        help_text="Definición de atributos personalizados para usuarios con este rol"
    )
    
    # Permisos específicos del rol (para uso futuro)
    permisos = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Permisos específicos del rol (para expansión futura)"
    )
    
    activo = models.BooleanField(
        default=True,
        help_text="Indica si este rol está activo y puede ser asignado a usuarios"
    )
    
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        unique_together = ('empresa', 'nombre')
        ordering = ['empresa', 'nombre']
    
    def __str__(self):
        return self.nombre
    
    def total_usuarios(self):
        """Retorna el número de usuarios que tienen este rol asignado"""
        return self.usuarios.count()
    
    def usuarios_activos(self):
        """Retorna el número de usuarios activos con este rol"""
        return self.usuarios.filter(is_active=True).count()