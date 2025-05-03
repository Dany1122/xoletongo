from django.shortcuts import render, get_object_or_404
from .models import Servicio,TipoServicio
from collections import defaultdict

# Create your views here.
def detalle_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, pk=servicio_id)
    return render(request, 'servicio.html', {'servicio': servicio, 'opacidad': 0.4})

def servicios_por_tipo(request):
    tipos_servicio = TipoServicio.objects.prefetch_related('subservicios')

    return render(request, 'servicios_por_tipo.html', {
        'tipos_servicio': tipos_servicio
    })
