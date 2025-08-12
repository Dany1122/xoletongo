from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from reservaciones.models import Reservacion
from empresas.models import Empresa
from django.utils.http import url_has_allowed_host_and_scheme
from django.shortcuts import resolve_url


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
            user = authenticate(
                request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user is not None:
                login(request, user)

                # Respeta ?next= si es seguro
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(next_url, {request.get_host()}):
                    return redirect(next_url)

                # Redirección por rol
                role = (getattr(user, 'rol', '') or '').strip()
                if role == 'Cliente':
                    return redirect('home')
                if role in ('Administrador', 'Empleado', 'Encargado'):
                    # Si tu panel está namespaced como adminpanel:admin_dashboard, usa esa forma:
                    try:
                        return redirect('adminpanel:admin_dashboard')
                    except Exception:
                        # fallback si no tienes namespace y el name es global
                        return redirect('admin_dashboard')

                # Fallback
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

