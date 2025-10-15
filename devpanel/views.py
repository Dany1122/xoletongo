# devpanel/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from empresas.models import Empresa

@login_required
def gestion_empresas(request):
    # Verificación de seguridad: solo superusuarios pueden acceder
    if not request.user.is_superuser:
        return redirect('admin_dashboard') # O a donde prefieras

    empresas = Empresa.objects.all().order_by('nombre')
    
    context = {
        'empresas': empresas
    }
    # Apuntamos a la nueva ruta de la plantilla
    return render(request, 'devpanel/gestion_empresas.html', context)



@login_required
def activar_empresa_dev(request, pk):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    try:
        empresa = Empresa.objects.get(pk=pk)
        # Guardamos el ID de la empresa en la sesión del usuario
        request.session['empresa_activa_id'] = empresa.id
        messages.success(request, f"Se ha activado el entorno de la empresa: {empresa.nombre}")
    except Empresa.DoesNotExist:
        messages.error(request, "La empresa que intentas activar no existe.")

    return redirect('dev_gestion_empresas')