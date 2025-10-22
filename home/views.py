from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.core.paginator import Paginator
from servicios.models import ImagenServicio
from empresas.models import Empresa
from devpanel.models import Pagina, Seccion
from adminpanel.models import Producto, CategoriaProducto, Pedido, ItemPedido
from decimal import Decimal
import json

def get_pagina_secciones(slug_pagina):
    """
    Helper function para obtener las secciones de una página
    """
    empresa = Empresa.objects.filter(activa=True).first()
    secciones = []
    
    if empresa:
        try:
            pagina = Pagina.objects.get(empresa=empresa, slug=slug_pagina)
            secciones = Seccion.objects.filter(pagina=pagina, activa=True).order_by('orden')
        except Pagina.DoesNotExist:
            pass
    
    return {
        'secciones': secciones,
        'empresa': empresa,
    }

# Create your views here.
class HomeView(View):
    def get(self, request):
        return render(request, 'index.html')

# Home
def index(request):
    context = get_pagina_secciones('home')
    return render(request, 'index.html', context)

def nosotros(request):
    context = get_pagina_secciones('nosotros')
    return render(request, 'nosotros.html', context)

# Servicios
def avistamiento(request):
    return render(request, 'home/servicios/avistamiento.html')

def agroturismo(request):
    return render(request, 'home/servicios/agroturismo.html')

def destilamiento(request):
    return render(request, 'home/servicios/destilamiento.html')

def gastroturismo(request):
    return render(request, 'home/servicios/gastroturismo.html')

def talleres(request):
    return render(request, 'home/servicios/talleres.html')

def senderismo(request):
    return render(request, 'home/servicios/senderismo.html')

def regenerativo(request):
    return render(request, 'home/servicios/regenerativo.html')

# Reservaciones
def hospedaje(request):
    return render(request, 'home/reservaciones/hospedaje.html')

def experiencia(request):
    return render(request, 'home/reservaciones/experiencia.html')

# Temporada de luciérnagas
def luciernagas_hospedaje(request):
    return render(request, 'home/reservaciones/luciernagas/hospedaje.html')

def luciernagas_transporte(request):
    return render(request, 'home/reservaciones/luciernagas/transporte.html')

def luciernagas_comida(request):
    return render(request, 'home/reservaciones/luciernagas/comida.html')

def luciernagas_cena(request):
    return render(request, 'home/reservaciones/luciernagas/cena.html')

def luciernagas_visita(request):
    return render(request, 'home/reservaciones/luciernagas/visita.html')

# Galería
def galeria(request):
    context = get_pagina_secciones('galeria')
    # Mantener funcionalidad de imágenes
    imagenes = ImagenServicio.objects.all()
    context['imagenes'] = imagenes
    return render(request, 'galeria.html', context)

# Contacto
def contacto(request):
    context = get_pagina_secciones('contacto')
    return render(request, 'contacto.html', context)


# ==================== VISTAS DE E-COMMERCE ====================

def productos(request):
    """Vista del catálogo de productos"""
    empresa = Empresa.objects.filter(activa=True).first()
    
    # Verificar si la empresa tiene productos habilitados
    if not empresa or not empresa.productos_habilitado:
        messages.info(request, 'El catálogo de productos no está disponible en este momento.')
        return redirect('home')
    
    # Obtener productos activos de la empresa
    productos_list = Producto.objects.filter(empresa=empresa, activo=True).select_related('categoria').order_by('-creado_en')
    
    # Filtro por categoría
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos_list = productos_list.filter(categoria_id=categoria_id)
    
    # Búsqueda
    q = request.GET.get('q', '').strip()
    if q:
        productos_list = productos_list.filter(nombre__icontains=q)
    
    # Paginación
    paginator = Paginator(productos_list, 12)  # 12 productos por página
    page_number = request.GET.get('page')
    productos_pagina = paginator.get_page(page_number)
    
    # Obtener categorías para el filtro
    categorias = CategoriaProducto.objects.filter(empresa=empresa)
    
    # Obtener carrito para mostrar contador
    carrito = request.session.get('carrito', {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    
    context = {
        'empresa': empresa,
        'productos': productos_pagina,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id,
        'q': q,
        'total_items_carrito': total_items,
    }
    return render(request, 'tienda/productos.html', context)


def producto_detalle(request, producto_id):
    """Vista del detalle de un producto"""
    empresa = Empresa.objects.filter(activa=True).first()
    
    # Verificar si la empresa tiene productos habilitados
    if not empresa or not empresa.productos_habilitado:
        messages.info(request, 'El catálogo de productos no está disponible en este momento.')
        return redirect('home')
    
    producto = get_object_or_404(Producto, id=producto_id, empresa=empresa, activo=True)
    
    # Productos relacionados (misma categoría)
    productos_relacionados = Producto.objects.filter(
        empresa=empresa,
        categoria=producto.categoria,
        activo=True
    ).exclude(id=producto.id)[:4]
    
    # Obtener carrito para mostrar contador
    carrito = request.session.get('carrito', {})
    total_items = sum(item['cantidad'] for item in carrito.values())
    
    context = {
        'empresa': empresa,
        'producto': producto,
        'productos_relacionados': productos_relacionados,
        'total_items_carrito': total_items,
    }
    return render(request, 'tienda/producto_detalle.html', context)


def agregar_al_carrito(request, producto_id):
    """Agregar producto al carrito (AJAX)"""
    empresa = Empresa.objects.filter(activa=True).first()
    
    # Verificar si la empresa tiene productos habilitados
    if not empresa or not empresa.productos_habilitado:
        messages.error(request, 'El catálogo de productos no está disponible.')
        return redirect('home')
    
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id, activo=True)
        cantidad = int(request.POST.get('cantidad', 1))
        
        # Obtener o crear carrito en sesión
        carrito = request.session.get('carrito', {})
        
        # Agregar o actualizar producto en carrito
        producto_key = str(producto.id)
        if producto_key in carrito:
            carrito[producto_key]['cantidad'] += cantidad
        else:
            carrito[producto_key] = {
                'nombre': producto.nombre,
                'precio': str(producto.precio),
                'cantidad': cantidad,
                'imagen': producto.imagen.url if producto.imagen else None,
            }
        
        # Guardar carrito en sesión
        request.session['carrito'] = carrito
        request.session.modified = True
        
        messages.success(request, f'"{producto.nombre}" agregado al carrito')
        
        # Redirigir a la página anterior o al catálogo
        return redirect(request.META.get('HTTP_REFERER', 'productos'))
    
    return redirect('productos')


def ver_carrito(request):
    """Vista del carrito de compras"""
    empresa = Empresa.objects.filter(activa=True).first()
    
    # Verificar si la empresa tiene productos habilitados
    if not empresa or not empresa.productos_habilitado:
        messages.info(request, 'El catálogo de productos no está disponible.')
        return redirect('home')
    
    carrito = request.session.get('carrito', {})
    
    # Calcular totales
    total = Decimal('0.00')
    items_carrito = []
    
    for producto_id, item in carrito.items():
        subtotal = Decimal(item['precio']) * item['cantidad']
        total += subtotal
        items_carrito.append({
            'id': producto_id,
            'nombre': item['nombre'],
            'precio': Decimal(item['precio']),
            'cantidad': item['cantidad'],
            'subtotal': subtotal,
            'imagen': item.get('imagen'),
        })
    
    context = {
        'empresa': empresa,
        'items_carrito': items_carrito,
        'total': total,
        'total_items': sum(item['cantidad'] for item in carrito.values()),
    }
    return render(request, 'tienda/carrito.html', context)


def actualizar_carrito(request, producto_id):
    """Actualizar cantidad de un producto en el carrito"""
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        producto_key = str(producto_id)
        
        if producto_key in carrito:
            accion = request.POST.get('accion')
            if accion == 'incrementar':
                carrito[producto_key]['cantidad'] += 1
            elif accion == 'decrementar':
                if carrito[producto_key]['cantidad'] > 1:
                    carrito[producto_key]['cantidad'] -= 1
                else:
                    del carrito[producto_key]
            elif accion == 'eliminar':
                del carrito[producto_key]
            
            request.session['carrito'] = carrito
            request.session.modified = True
            messages.success(request, 'Carrito actualizado')
        
        return redirect('ver_carrito')
    
    return redirect('ver_carrito')


def checkout(request):
    """Vista de checkout"""
    empresa = Empresa.objects.filter(activa=True).first()
    
    # Verificar si la empresa tiene productos habilitados
    if not empresa or not empresa.productos_habilitado:
        messages.info(request, 'El catálogo de productos no está disponible.')
        return redirect('home')
    
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('productos')
    
    # Calcular totales
    total = Decimal('0.00')
    items_carrito = []
    
    for producto_id, item in carrito.items():
        subtotal = Decimal(item['precio']) * item['cantidad']
        total += subtotal
        items_carrito.append({
            'id': producto_id,
            'nombre': item['nombre'],
            'precio': Decimal(item['precio']),
            'cantidad': item['cantidad'],
            'subtotal': subtotal,
        })
    
    context = {
        'empresa': empresa,
        'items_carrito': items_carrito,
        'total': total,
    }
    return render(request, 'tienda/checkout.html', context)


def procesar_pedido(request):
    """Procesar el pedido y guardarlo en la base de datos"""
    if request.method == 'POST':
        empresa = Empresa.objects.filter(activa=True).first()
        
        # Verificar si la empresa tiene productos habilitados
        if not empresa or not empresa.productos_habilitado:
            messages.error(request, 'El catálogo de productos no está disponible.')
            return redirect('home')
        
        carrito = request.session.get('carrito', {})
        
        if not carrito:
            messages.error(request, 'Tu carrito está vacío')
            return redirect('productos')
        
        # Obtener datos del formulario
        nombre_cliente = request.POST.get('nombre_cliente')
        email_cliente = request.POST.get('email_cliente')
        telefono_cliente = request.POST.get('telefono_cliente')
        direccion_entrega = request.POST.get('direccion_entrega')
        notas = request.POST.get('notas', '')
        metodo_pago = request.POST.get('metodo_pago', 'efectivo')
        
        # Calcular total
        total = Decimal('0.00')
        for item in carrito.values():
            total += Decimal(item['precio']) * item['cantidad']
        
        # Crear pedido
        pedido = Pedido.objects.create(
            empresa=empresa,
            usuario=request.user if request.user.is_authenticated else None,
            nombre_cliente=nombre_cliente,
            email_cliente=email_cliente,
            telefono_cliente=telefono_cliente,
            direccion_entrega=direccion_entrega,
            notas=notas,
            total=total,
            metodo_pago=metodo_pago,
        )
        
        # Crear items del pedido
        for producto_id, item in carrito.items():
            producto = Producto.objects.get(id=producto_id)
            ItemPedido.objects.create(
                pedido=pedido,
                producto=producto,
                nombre_producto=item['nombre'],
                precio_unitario=Decimal(item['precio']),
                cantidad=item['cantidad'],
            )
        
        # Limpiar carrito
        request.session['carrito'] = {}
        request.session.modified = True
        
        messages.success(request, f'¡Pedido #{pedido.numero_pedido} realizado exitosamente!')
        
        # Redirigir a página de confirmación
        return redirect('confirmacion_pedido', pedido_id=pedido.id)
    
    return redirect('checkout')


def confirmacion_pedido(request, pedido_id):
    """Vista de confirmación del pedido"""
    empresa = Empresa.objects.filter(activa=True).first()
    
    # Verificar si la empresa tiene productos habilitados
    if not empresa or not empresa.productos_habilitado:
        messages.info(request, 'El catálogo de productos no está disponible.')
        return redirect('home')
    
    pedido = get_object_or_404(Pedido, id=pedido_id, empresa=empresa)
    
    context = {
        'empresa': empresa,
        'pedido': pedido,
    }
    return render(request, 'tienda/confirmacion.html', context)


