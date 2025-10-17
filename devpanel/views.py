# devpanel/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from empresas.models import Empresa
from .models import CustomAttribute
from .forms import EmpresaForm, CustomAttributeForm

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

@login_required
def gestion_modelos(request):
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    # Verificamos si hay una empresa activa en la sesión
    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id:
        messages.warning(request, "Por favor, activa una empresa para poder gestionar sus modelos.")
        return redirect('dev_gestion_empresas')

    # Obtenemos solo los atributos de la empresa activa
    empresa_activa = Empresa.objects.get(id=empresa_activa_id)
    atributos = CustomAttribute.objects.filter(empresa=empresa_activa)

    form = CustomAttributeForm()

    context = {
        'empresa_activa': empresa_activa,
        'atributos': atributos,
        'form': form
    }
    return render(request, 'devpanel/gestion_modelos.html', context)

def crear_atributo(request):
    if not request.user.is_superuser:
        return redirect('dev_gestion_empresas')

    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id:
        messages.error(request, "No hay una empresa activa para asignarle el atributo.")
        return redirect('dev_gestion_empresas')

    if request.method == 'POST':
        form = CustomAttributeForm(request.POST)
        if form.is_valid():
            nuevo_atributo = form.save(commit=False)
            nuevo_atributo.empresa_id = empresa_activa_id
            nuevo_atributo.save()
            messages.success(request, f"Se ha creado el atributo '{nuevo_atributo.name}'.")
        else:
            messages.error(request, "Error al crear el atributo. Revisa los datos.")
    
    return redirect('dev_gestion_modelos')