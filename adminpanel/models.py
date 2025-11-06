from django.db import models
from django.contrib.auth import get_user_model
from empresas.models import Empresa 

# Create your models here.
class Venta(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado')
    ]

    titulo = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"{self.titulo} (${self.monto})"

User = get_user_model()

class Novedad(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    accion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.accion}"
    
class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, blank=True)
    perecedero = models.BooleanField(default=False)
    fecha_caducidad = models.DateField(null=True, blank=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, unique=True, default='sku-temp')
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    atributos_personalizados = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.nombre


# ==================== MODELOS PARA E-COMMERCE ====================

class Pedido(models.Model):
    """
    Modelo para gestionar pedidos de productos
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_proceso', 'En Proceso'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('tarjeta', 'Tarjeta (en tienda)'),
    ]
    
    # Relaciones
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='pedidos')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    
    # Información del cliente
    nombre_cliente = models.CharField(max_length=200)
    email_cliente = models.EmailField()
    telefono_cliente = models.CharField(max_length=20)
    direccion_entrega = models.TextField()
    notas = models.TextField(blank=True, help_text="Notas adicionales del cliente")
    
    # Información del pedido
    numero_pedido = models.CharField(max_length=50, unique=True, editable=False)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='efectivo')
    
    # Fechas
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_entrega_estimada = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_pedido']
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
    
    def __str__(self):
        return f"Pedido #{self.numero_pedido} - {self.nombre_cliente}"
    
    def save(self, *args, **kwargs):
        if not self.numero_pedido:
            # Generar número de pedido único
            import uuid
            from datetime import datetime
            fecha_str = datetime.now().strftime('%Y%m%d')
            codigo_unico = str(uuid.uuid4().hex[:6]).upper()
            self.numero_pedido = f"PED-{fecha_str}-{codigo_unico}"
        super().save(*args, **kwargs)
    
    def calcular_total(self):
        """Calcula el total sumando todos los items"""
        total = sum(item.subtotal() for item in self.items.all())
        return total


class ItemPedido(models.Model):
    """
    Modelo para los productos individuales dentro de un pedido
    """
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    
    # Información al momento de la compra (puede cambiar después)
    nombre_producto = models.CharField(max_length=200, help_text="Nombre del producto al momento de la compra")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio al momento de la compra")
    cantidad = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'
    
    def __str__(self):
        return f"{self.cantidad}x {self.nombre_producto} - Pedido #{self.pedido.numero_pedido}"
    
    def subtotal(self):
        """Calcula el subtotal de este item"""
        return self.precio_unitario * self.cantidad
