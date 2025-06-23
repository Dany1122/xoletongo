from empresas.models import Empresa

def empresa_context(request):
    return {
        'empresa_activa': Empresa.objects.filter(activa=True).first()
    }