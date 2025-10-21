from django.shortcuts import render, get_object_or_404
from .models import Servicio,TipoServicio,ImagenServicio
from collections import defaultdict
from django.db.models import Prefetch
from empresas.models import Empresa
from devpanel.models import Pagina, Seccion

# Create your views here.
def detalle_servicio(request, servicio_id):
    servicio = (
        Servicio.objects
        .select_related('servicio', 'empresa')
        .prefetch_related(
            Prefetch('imagenes', queryset=ImagenServicio.objects.order_by('orden', 'id'))
        )
        .get(pk=servicio_id)
    )
    return render(request, 'servicio.html', {
        'servicio': servicio,
        'opacidad': 0.4
    })

def servicios_por_tipo(request):
    """
    Vista dinámica para la página de servicios.
    Carga las secciones desde la BD y también pasa los tipos de servicio.
    """
    # Obtener empresa activa
    empresa = Empresa.objects.filter(activa=True).first()
    
    # Obtener servicios y tipos (OBLIGATORIO para la funcionalidad)
    servicios_qs = (
        Servicio.objects
        .select_related('servicio', 'empresa')
        .prefetch_related(
            Prefetch('imagenes', queryset=ImagenServicio.objects.order_by('orden', 'id'))
        )
        .order_by('titulo')
    )

    tipos_servicio = (
        TipoServicio.objects
        .order_by('nombre')
        .prefetch_related(
            Prefetch('subservicios', queryset=servicios_qs)
        )
    )
    
    # Obtener secciones dinámicas
    secciones = []
    if empresa:
        try:
            pagina = Pagina.objects.get(empresa=empresa, slug='servicios')
            secciones = Seccion.objects.filter(pagina=pagina, activa=True).order_by('orden')
        except Pagina.DoesNotExist:
            pass
    
    return render(request, 'servicios_por_tipo.html', {
        'tipos_servicio': tipos_servicio,
        'secciones': secciones,
        'empresa': empresa
    })