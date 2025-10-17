from django.shortcuts import render, get_object_or_404
from .models import Servicio,TipoServicio,ImagenServicio
from collections import defaultdict
from django.db.models import Prefetch

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

    return render(request, 'servicios_por_tipo.html', {
        'tipos_servicio': tipos_servicio
    })