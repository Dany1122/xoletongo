from django.shortcuts import render, get_object_or_404
from .models import Servicio,TipoServicio

# Create your views here.
def detalle_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, pk=servicio_id)
    return render(request, 'servicio.html', {'servicio': servicio, 'opacidad': 0.4})

def servicios_por_tipo(request):
    hospedaje = Servicio.objects.filter(servicio__tipo='hospedaje')
    visita = Servicio.objects.filter(servicio__tipo='visita')
    restaurante = Servicio.objects.filter(servicio__tipo='restaurante')
    
    return render(request, 'servicios_por_tipo.html', {
        'hospedaje': hospedaje,
        'visita': visita,
        'restaurante': restaurante,
    })
