from django.shortcuts import render
from django.views import View
from servicios.models import ImagenServicio
from empresas.models import Empresa
from devpanel.models import Pagina, Seccion

def get_pagina_secciones(slug_pagina):
    """
    Helper function para obtener las secciones de una página
    """
    empresa = Empresa.objects.filter(activa=True).first()
    secciones = []
    
    if empresa:
        try:
            pagina = Pagina.objects.get(empresa=empresa, slug=slug_pagina)
            secciones = Seccion.objects.filter(pagina=pagina, activa=True).order_by('orden')
        except Pagina.DoesNotExist:
            pass
    
    return {
        'secciones': secciones,
        'empresa': empresa,
    }

# Create your views here.
class HomeView(View):
    def get(self, request):
        return render(request, 'index.html')

# Home
def index(request):
    context = get_pagina_secciones('home')
    return render(request, 'index.html', context)

def nosotros(request):
    context = get_pagina_secciones('nosotros')
    return render(request, 'nosotros.html', context)

# Servicios
def avistamiento(request):
    return render(request, 'home/servicios/avistamiento.html')

def agroturismo(request):
    return render(request, 'home/servicios/agroturismo.html')

def destilamiento(request):
    return render(request, 'home/servicios/destilamiento.html')

def gastroturismo(request):
    return render(request, 'home/servicios/gastroturismo.html')

def talleres(request):
    return render(request, 'home/servicios/talleres.html')

def senderismo(request):
    return render(request, 'home/servicios/senderismo.html')

def regenerativo(request):
    return render(request, 'home/servicios/regenerativo.html')

# Reservaciones
def hospedaje(request):
    return render(request, 'home/reservaciones/hospedaje.html')

def experiencia(request):
    return render(request, 'home/reservaciones/experiencia.html')

# Temporada de luciérnagas
def luciernagas_hospedaje(request):
    return render(request, 'home/reservaciones/luciernagas/hospedaje.html')

def luciernagas_transporte(request):
    return render(request, 'home/reservaciones/luciernagas/transporte.html')

def luciernagas_comida(request):
    return render(request, 'home/reservaciones/luciernagas/comida.html')

def luciernagas_cena(request):
    return render(request, 'home/reservaciones/luciernagas/cena.html')

def luciernagas_visita(request):
    return render(request, 'home/reservaciones/luciernagas/visita.html')

# Galería
def galeria(request):
    context = get_pagina_secciones('galeria')
    # Mantener funcionalidad de imágenes
    imagenes = ImagenServicio.objects.all()
    context['imagenes'] = imagenes
    return render(request, 'galeria.html', context)

# Contacto
def contacto(request):
    context = get_pagina_secciones('contacto')
    return render(request, 'contacto.html', context)


