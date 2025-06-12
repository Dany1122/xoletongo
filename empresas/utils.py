from django.core.cache import cache
from .models import Empresa

def obtener_empresa_activa():
    """
    Devuelve la instancia de Empresa donde activa=True.
    Cachea el resultado durante 60 segundos para evitar múltiples consultas.
    """
    cache_key = "empresa_activa"
    empresa = cache.get(cache_key)
    if empresa is None:
        empresa = Empresa.objects.filter(activa=True).first()
        cache.set(cache_key, empresa, timeout=60)
    return empresa