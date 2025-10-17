# devpanel/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from empresas.models import Empresa
from .forms import EmpresaForm

@login_required
def gestion_empresas(request):
    # Verificación de seguridad: solo superusuarios pueden acceder
    if not request.user.is_superuser:
        return redirect('admin_dashboard') # O a donde prefieras

    empresas = Empresa.objects.all().order_by('nombre')
    form = EmpresaForm()
    
    context = {
        'empresas': empresas,
        'form': form,
    }
    # Apuntamos a la nueva ruta de la plantilla
    return render(request, 'devpanel/gestion_empresas.html', context)

@login_required
def crear_empresa(request):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            nueva_empresa = form.save()
            messages.success(request, f"La empresa '{nueva_empresa.nombre}' ha sido creada exitosamente.")
        else:
            messages.error(request, "Hubo un error al crear la empresa. Revisa los datos.")
    
    return redirect('dev_gestion_empresas')

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

@login_required
def editar_empresa(request, pk):
    # Security check: only superusers can edit
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    # Get the specific enterprise we want to edit
    empresa = get_object_or_404(Empresa, pk=pk)
    
    # This view only handles POST requests from the modal
    if request.method == 'POST':
        # Populate the form with the submitted data and the existing enterprise instance
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, f"Se han guardado los cambios para la empresa '{empresa.nombre}'.")
        else:
            messages.error(request, "Hubo un error al guardar los cambios.")
    
    # After processing, always redirect back to the list
    return redirect('dev_gestion_empresas')