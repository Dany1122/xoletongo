from django.contrib import admin
from .models import Producto, CategoriaProducto, Pedido, ItemPedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('subtotal',)
    
    def subtotal(self, obj):
        return f"${obj.subtotal():.2f}"
    subtotal.short_description = 'Subtotal'


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero_pedido', 'nombre_cliente', 'empresa', 'total', 'estado', 'fecha_pedido')
    list_filter = ('estado', 'empresa', 'fecha_pedido')
    search_fields = ('numero_pedido', 'nombre_cliente', 'email_cliente', 'telefono_cliente')
    readonly_fields = ('numero_pedido', 'fecha_pedido', 'fecha_actualizacion')
    inlines = [ItemPedidoInline]
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('numero_pedido', 'empresa', 'usuario', 'estado', 'metodo_pago', 'total')
        }),
        ('Información del Cliente', {
            'fields': ('nombre_cliente', 'email_cliente', 'telefono_cliente', 'direccion_entrega', 'notas')
        }),
        ('Fechas', {
            'fields': ('fecha_pedido', 'fecha_actualizacion', 'fecha_entrega_estimada')
        }),
    )


admin.site.register(Producto)
admin.site.register(CategoriaProducto)
