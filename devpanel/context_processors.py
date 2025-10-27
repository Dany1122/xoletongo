# devpanel/context_processors.py
from empresas.models import Empresa

def empresa_activa_processor(request):
    empresa_activa_id = request.session.get('empresa_activa_id')
    if empresa_activa_id:
        try:
            empresa = Empresa.objects.get(id=empresa_activa_id)
            return {'empresa_activa_nombre': empresa.nombre}
        except Empresa.DoesNotExist:
            return {}
    return {}