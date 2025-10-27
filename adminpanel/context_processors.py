from empresas.models import Empresa

def empresa_context(request):
    """
    Context processor que inyecta la empresa activa y su tema en todos los templates
    """
    empresa = Empresa.objects.select_related('tema').filter(activa=True).first()
    
    context = {
        'empresa_activa': empresa,
    }
    
    # Si la empresa tiene un tema asignado, lo inyectamos también
    if empresa and empresa.tema:
        context['tema'] = empresa.tema
    else:
        # Valores por defecto si no hay tema
        context['tema'] = None
    
    return context