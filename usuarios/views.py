from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from reservaciones.models import Reservacion
from empresas.models import Empresa

def registro_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            empresa_activa = Empresa.objects.filter(activa=True).first()
            if not empresa_activa:
                messages.error(request, "No hay una empresa activa configurada.")
                return redirect('registro')

            user = form.save(commit=False)
            user.empresa = empresa_activa
            user.save()

            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registro.html', {'form': form})
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'),
                                password=form.cleaned_data.get('password'))
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Sesión cerrada exitosamente')
    return redirect('login')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def perfil_view(request):
    reservaciones = Reservacion.objects.filter(email_cliente=request.user.email).order_by('-fecha_reserva')
    return render(request, 'perfil.html', {'reservaciones': reservaciones})

