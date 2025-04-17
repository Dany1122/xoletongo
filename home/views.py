from django.shortcuts import render
from django.views import View

# Create your views here.
class HomeView(View):
    def get(self, request):
        return render(request, 'index.html')
    
from django.shortcuts import render

# Home
def index(request):
    return render(request, 'home/index.html')

def nosotros(request):
    return render(request, 'home/nosotros.html')

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
    return render(request, 'home/galeria.html')

# Contacto
def contacto(request):
    return render(request, 'home/contacto.html')


#Login
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # o a donde quieras redirigir
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')

    return render(request, 'login.html')

