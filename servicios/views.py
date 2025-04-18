from django.shortcuts import render, get_object_or_404
from .models import Servicio,TipoServicio

# Create your views here.
def detalle_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, pk=servicio_id)
    return render(request, 'servicio.html', {'servicio': servicio, 'opacidad': 0.4})

def listar_subservicios_por_tipo(request, tipo_servicio):
    tipoServicio = get_object_or_404(TipoServicio, tipo=tipo_servicio.lower())
    subservicios = Servicio.objects.filter(servicio=tipoServicio)
    return render(request, 'servicios_por_tipo.html', {
        'subservicios': subservicios,
        'servicio': tipoServicio
    })