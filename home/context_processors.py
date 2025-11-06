from devpanel.models import Pagina, Seccion
from empresas.models import Empresa


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


def footer_context(request):
    """
    Context processor para el footer dinámico
    Añade las secciones del footer a todas las templates
    """
    empresa = Empresa.objects.filter(activa=True).first()
    footer_secciones = []
    
    if empresa:
        try:
            pagina_footer = Pagina.objects.get(slug='footer', empresa=empresa, activa=True)
            footer_secciones = Seccion.objects.filter(
                pagina=pagina_footer,
                activa=True
            ).order_by('orden')
        except Pagina.DoesNotExist:
            pass
    
    return {
        'footer_secciones': footer_secciones,
    }

