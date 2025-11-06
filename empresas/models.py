from django.db import models
from django.core.validators import RegexValidator

# Create your models here.

class Tema(models.Model):
    """
    Modelo para personalización visual de cada empresa
    """
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre del tema (ej: 'Moderno', 'Clásico')")
    
    # Colores principales
    color_primario = models.CharField(
        max_length=7, 
        default='#4CAF50',
        validators=[RegexValidator(regex='^#[0-9A-Fa-f]{6}$', message='Debe ser un color hexadecimal válido (ej: #4CAF50)')],
        help_text="Color principal del tema (hexadecimal)"
    )
    color_secundario = models.CharField(
        max_length=7,
        default='#2196F3',
        validators=[RegexValidator(regex='^#[0-9A-Fa-f]{6}$', message='Debe ser un color hexadecimal válido')],
        help_text="Color secundario del tema"
    )
    color_acento = models.CharField(
        max_length=7,
        default='#FF9800',
        validators=[RegexValidator(regex='^#[0-9A-Fa-f]{6}$', message='Debe ser un color hexadecimal válido')],
        help_text="Color de acento para botones y enlaces"
    )
    color_texto = models.CharField(
        max_length=7,
        default='#333333',
        validators=[RegexValidator(regex='^#[0-9A-Fa-f]{6}$', message='Debe ser un color hexadecimal válido')],
        help_text="Color del texto principal"
    )
    color_fondo = models.CharField(
        max_length=7,
        default='#FFFFFF',
        validators=[RegexValidator(regex='^#[0-9A-Fa-f]{6}$', message='Debe ser un color hexadecimal válido')],
        help_text="Color de fondo principal"
    )
    
    # Tipografía
    FUENTE_CHOICES = [
        ('Arial', 'Arial'),
        ('Helvetica', 'Helvetica'),
        ('Roboto', 'Roboto'),
        ('Open Sans', 'Open Sans'),
        ('Lato', 'Lato'),
        ('Montserrat', 'Montserrat'),
        ('Georgia', 'Georgia'),
        ('Times New Roman', 'Times New Roman'),
    ]
    fuente_principal = models.CharField(max_length=50, choices=FUENTE_CHOICES, default='Roboto')
    fuente_secundaria = models.CharField(max_length=50, choices=FUENTE_CHOICES, default='Open Sans')
    
    # Layout y estilo
    ESTILO_CHOICES = [
        ('moderno', 'Moderno'),
        ('clasico', 'Clásico'),
        ('minimalista', 'Minimalista'),
        ('corporativo', 'Corporativo'),
    ]
    estilo_layout = models.CharField(max_length=20, choices=ESTILO_CHOICES, default='moderno')
    
    # Estilo de navbar
    NAVBAR_ESTILO_CHOICES = [
        ('transparente_scroll', 'Transparente con scroll'),
        ('color_primario', 'Siempre color primario'),
        ('negro', 'Siempre negro'),
    ]
    navbar_estilo = models.CharField(
        max_length=30,
        choices=NAVBAR_ESTILO_CHOICES,
        default='color_primario',
        help_text='Estilo de la barra de navegación'
    )
    
    # Imágenes del tema
    logo_header = models.ImageField(upload_to='temas/logos/', null=True, blank=True, help_text="Logo para el header")
    imagen_hero = models.ImageField(upload_to='temas/hero/', null=True, blank=True, help_text="Imagen principal del home")
    favicon = models.ImageField(upload_to='temas/favicons/', null=True, blank=True)
    
    # Metadata
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Tema"
        verbose_name_plural = "Temas"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Empresa(models.Model):
    # Información básica
    nombre = models.CharField(max_length=100)
    nombre_titular = models.CharField(max_length=100)
    correo_contacto = models.EmailField()
    telefono = models.CharField(max_length=20)
    ubicacion = models.CharField(max_length=255)
    
    # Información bancaria
    cuenta_bancaria = models.CharField(max_length=18)
    clabe = models.CharField(max_length=18)
    numero_terjeta = models.CharField(max_length=16)
    
    # Branding y personalización
    logotipo = models.ImageField(upload_to='empresas/logos/', null=True, blank=True)
    sitio_web = models.URLField(blank=True, null=True)
    tema = models.ForeignKey(Tema, on_delete=models.SET_NULL, null=True, blank=True, related_name='empresas', help_text="Tema visual para el sitio")
    
    # Multi-sitio / Dominios
    subdominio = models.SlugField(
        max_length=100, 
        unique=True, 
        null=True, 
        blank=True,
        help_text="Subdominio para acceder al sitio (ej: 'xoletongo' para xoletongo.midominio.com)"
    )
    dominio_personalizado = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        help_text="Dominio propio de la empresa (ej: 'www.xoletongo.com')"
    )
    
    # Estado y configuración
    activa = models.BooleanField(default=False, help_text="Empresa actualmente activa en el sistema")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    # Módulos habilitados
    productos_habilitado = models.BooleanField(
        default=False, 
        help_text="Habilitar tienda/catálogo de productos para esta empresa"
    )
    servicios_habilitado = models.BooleanField(
        default=True,
        help_text="Habilitar visualización y gestión de servicios"
    )
    resenas_habilitado = models.BooleanField(
        default=True,
        help_text="Habilitar sistema de reseñas para productos y servicios"
    )
    
    # Configuración SMTP
    smtp_host = models.CharField(max_length=150, blank=True, null=True, help_text="Servidor SMTP (p. ej. smtp.gmail.com)")
    smtp_port = models.PositiveIntegerField(default=587, help_text="Puerto SMTP (p. ej. 587 para TLS, 465 para SSL)")
    smtp_user = models.CharField(max_length=100, blank=True, null=True, help_text="Usuario SMTP (p. ej. nombre@dominio.com)")
    smtp_password = models.CharField(max_length=100, blank=True, null=True, help_text="Contraseña SMTP (o contraseña de aplicación)")
    smtp_use_tls = models.BooleanField(default=True, help_text="Activar TLS al enviar correo")
    smtp_use_ssl = models.BooleanField(default=False, help_text="Activar SSL al enviar correo")
    
    class Meta:
        verbose_name_plural = "Empresas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
    
    def get_tema(self):
        """Retorna el tema de la empresa o un tema por defecto"""
        return self.tema if self.tema else None