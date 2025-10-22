def carrito_context(request):
    """
    Context processor para el carrito de compras
    Añade el contador de items del carrito a todas las templates
    """
    carrito = request.session.get('carrito', {})
    total_items_carrito = sum(item['cantidad'] for item in carrito.values())
    
    return {
        'total_items_carrito': total_items_carrito,
        'carrito': carrito,
    }

