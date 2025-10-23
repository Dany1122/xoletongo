# devpanel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from empresas.models import Empresa
from .models import CustomAttribute, Pagina, Seccion, Rol
from .forms import EmpresaForm, CustomAttributeForm, SeccionBaseForm, SeccionConfigForm, RolForm, AtributoSchemaForm, TemaForm, SuperuserForm, SuperuserEditForm
from django.db.models import F, Count
from django.http import JsonResponse
from empresas.models import Tema
from usuarios.models import CustomUser

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

    # Obtenemos los atributos de la empresa activa separados por modelo
    empresa_activa = Empresa.objects.get(id=empresa_activa_id)
    atributos_producto = CustomAttribute.objects.filter(empresa=empresa_activa, target_model='Producto')
    atributos_servicio = CustomAttribute.objects.filter(empresa=empresa_activa, target_model='Servicio')

    form = CustomAttributeForm()

    context = {
        'empresa_activa': empresa_activa,
        'atributos_producto': atributos_producto,
        'atributos_servicio': atributos_servicio,
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

@login_required
def editar_atributo(request, pk):
    if not request.user.is_superuser:
        return redirect('dev_gestion_empresas')

    atributo = get_object_or_404(CustomAttribute, pk=pk)
    
    # Verificar que el atributo pertenece a la empresa activa
    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id or atributo.empresa_id != empresa_activa_id:
        messages.error(request, "No tienes permiso para editar este atributo.")
        return redirect('dev_gestion_modelos')

    if request.method == 'POST':
        form = CustomAttributeForm(request.POST, instance=atributo)
        if form.is_valid():
            form.save()
            messages.success(request, f"El atributo '{atributo.name}' ha sido actualizado.")
        else:
            messages.error(request, "Error al actualizar el atributo.")
    
    return redirect('dev_gestion_modelos')

@login_required
def eliminar_atributo(request, pk):
    if not request.user.is_superuser:
        return redirect('dev_gestion_empresas')

    atributo = get_object_or_404(CustomAttribute, pk=pk)
    
    # Verificar que el atributo pertenece a la empresa activa
    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id or atributo.empresa_id != empresa_activa_id:
        messages.error(request, "No tienes permiso para eliminar este atributo.")
        return redirect('dev_gestion_modelos')

    if request.method == 'POST':
        nombre_atributo = atributo.name
        atributo.delete()
        messages.success(request, f"El atributo '{nombre_atributo}' ha sido eliminado.")
    
    return redirect('dev_gestion_modelos')

@login_required
def gestion_secciones(request):
    """Vista principal de gestión de secciones - lista de páginas"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id:
        messages.warning(request, "Por favor, activa una empresa para poder gestionar sus secciones.")
        return redirect('dev_gestion_empresas')

    empresa_activa = Empresa.objects.get(id=empresa_activa_id)
    paginas = Pagina.objects.filter(empresa=empresa_activa).prefetch_related('secciones')

    context = {
        'empresa_activa': empresa_activa,
        'paginas': paginas,
    }
    return render(request, 'devpanel/gestion_secciones.html', context)

@login_required
def gestion_secciones_pagina(request, slug_pagina):
    """Vista detallada de las secciones de una página específica"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id:
        messages.warning(request, "Por favor, activa una empresa para poder gestionar sus secciones.")
        return redirect('dev_gestion_empresas')

    empresa_activa = Empresa.objects.get(id=empresa_activa_id)
    pagina = get_object_or_404(Pagina, empresa=empresa_activa, slug=slug_pagina)
    secciones = Seccion.objects.filter(pagina=pagina).order_by('orden')

    context = {
        'empresa_activa': empresa_activa,
        'pagina': pagina,
        'secciones': secciones,
    }
    return render(request, 'devpanel/gestion_secciones_detalle.html', context)

@login_required
def crear_seccion(request, slug_pagina):
    """Crear una nueva sección"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id:
        messages.error(request, "No hay una empresa activa.")
        return redirect('dev_gestion_empresas')

    empresa_activa = Empresa.objects.get(id=empresa_activa_id)
    pagina = get_object_or_404(Pagina, empresa=empresa_activa, slug=slug_pagina)

    if request.method == 'POST':
        form = SeccionBaseForm(request.POST)
        if form.is_valid():
            seccion = form.save(commit=False)
            seccion.pagina = pagina
            # Asignar el siguiente orden disponible
            max_orden = Seccion.objects.filter(pagina=pagina).aggregate(max_orden=F('orden'))['max_orden']
            seccion.orden = (max_orden or 0) + 1
            seccion.configuracion = {}  # Configuración vacía por defecto
            seccion.save()
            messages.success(request, f"Sección '{seccion.titulo or seccion.get_tipo_display()}' creada exitosamente.")
            return redirect('dev_gestion_secciones_pagina', slug_pagina=slug_pagina)
        else:
            messages.error(request, "Error al crear la sección.")
    
    return redirect('dev_gestion_secciones_pagina', slug_pagina=slug_pagina)

@login_required
def editar_seccion(request, pk):
    """Editar una sección existente"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    seccion = get_object_or_404(Seccion, pk=pk)
    empresa_activa_id = request.session.get('empresa_activa_id')
    
    if not empresa_activa_id or seccion.pagina.empresa_id != empresa_activa_id:
        messages.error(request, "No tienes permiso para editar esta sección.")
        return redirect('dev_gestion_secciones')

    if request.method == 'POST':
        # Formulario para datos básicos
        form_base = SeccionBaseForm(request.POST, instance=seccion)
        # Formulario para configuración JSON
        form_config = SeccionConfigForm(request.POST, seccion=seccion)
        
        if form_base.is_valid() and form_config.is_valid():
            seccion = form_base.save(commit=False)
            seccion.configuracion = form_config.cleaned_data['configuracion_json']
            seccion.save()
            messages.success(request, f"Sección '{seccion.titulo or seccion.get_tipo_display()}' actualizada.")
            return redirect('dev_gestion_secciones_pagina', slug_pagina=seccion.pagina.slug)
        else:
            messages.error(request, "Error al actualizar la sección. Verifica el JSON.")
    
    return redirect('dev_gestion_secciones_pagina', slug_pagina=seccion.pagina.slug)

@login_required
def eliminar_seccion(request, pk):
    """Eliminar una sección"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    seccion = get_object_or_404(Seccion, pk=pk)
    empresa_activa_id = request.session.get('empresa_activa_id')
    
    if not empresa_activa_id or seccion.pagina.empresa_id != empresa_activa_id:
        messages.error(request, "No tienes permiso para eliminar esta sección.")
        return redirect('dev_gestion_secciones')

    if request.method == 'POST':
        slug_pagina = seccion.pagina.slug
        nombre_seccion = seccion.titulo or seccion.get_tipo_display()
        seccion.delete()
        messages.success(request, f"Sección '{nombre_seccion}' eliminada exitosamente.")
        return redirect('dev_gestion_secciones_pagina', slug_pagina=slug_pagina)
    
    return redirect('dev_gestion_secciones')

@login_required
def cambiar_orden_seccion(request, pk, direccion):
    """Cambiar el orden de una sección (subir o bajar)"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    seccion = get_object_or_404(Seccion, pk=pk)
    empresa_activa_id = request.session.get('empresa_activa_id')
    
    if not empresa_activa_id or seccion.pagina.empresa_id != empresa_activa_id:
        messages.error(request, "No tienes permiso para reordenar esta sección.")
        return redirect('dev_gestion_secciones')

    if direccion == 'subir':
        # Buscar la sección anterior
        seccion_anterior = Seccion.objects.filter(
            pagina=seccion.pagina,
            orden__lt=seccion.orden
        ).order_by('-orden').first()
        
        if seccion_anterior:
            # Intercambiar órdenes
            seccion.orden, seccion_anterior.orden = seccion_anterior.orden, seccion.orden
            seccion.save()
            seccion_anterior.save()
            messages.success(request, "Sección movida hacia arriba.")
        else:
            messages.warning(request, "La sección ya está en la primera posición.")
    
    elif direccion == 'bajar':
        # Buscar la sección siguiente
        seccion_siguiente = Seccion.objects.filter(
            pagina=seccion.pagina,
            orden__gt=seccion.orden
        ).order_by('orden').first()
        
        if seccion_siguiente:
            # Intercambiar órdenes
            seccion.orden, seccion_siguiente.orden = seccion_siguiente.orden, seccion.orden
            seccion.save()
            seccion_siguiente.save()
            messages.success(request, "Sección movida hacia abajo.")
        else:
            messages.warning(request, "La sección ya está en la última posición.")
    
    return redirect('dev_gestion_secciones_pagina', slug_pagina=seccion.pagina.slug)

@login_required
def toggle_seccion_activa(request, pk):
    """Activar o desactivar una sección"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')

    seccion = get_object_or_404(Seccion, pk=pk)
    empresa_activa_id = request.session.get('empresa_activa_id')
    
    if not empresa_activa_id or seccion.pagina.empresa_id != empresa_activa_id:
        messages.error(request, "No tienes permiso para modificar esta sección.")
        return redirect('dev_gestion_secciones')

    seccion.activa = not seccion.activa
    seccion.save()
    estado = "activada" if seccion.activa else "desactivada"
    messages.success(request, f"Sección '{seccion.titulo or seccion.get_tipo_display()}' {estado}.")
    
    return redirect('dev_gestion_secciones_pagina', slug_pagina=seccion.pagina.slug)


# ==================== GESTIÓN DE ROLES ====================

@login_required
def gestion_roles(request):
    """Vista principal de gestión de roles"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id:
        messages.warning(request, "Por favor, activa una empresa para poder gestionar sus roles.")
        return redirect('dev_gestion_empresas')
    
    empresa_activa = Empresa.objects.get(id=empresa_activa_id)
    roles = Rol.objects.filter(empresa=empresa_activa).annotate(
        num_usuarios=Count('usuarios')
    ).order_by('nombre')
    
    context = {
        'empresa_activa': empresa_activa,
        'roles': roles,
    }
    return render(request, 'devpanel/gestion_roles.html', context)


@login_required
def crear_rol(request):
    """Crear un nuevo rol"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id:
        messages.error(request, "No hay una empresa activa.")
        return redirect('dev_gestion_empresas')
    
    empresa_activa = Empresa.objects.get(id=empresa_activa_id)
    
    if request.method == 'POST':
        form = RolForm(request.POST, empresa=empresa_activa)
        if form.is_valid():
            rol = form.save(commit=False)
            rol.empresa = empresa_activa
            rol.atributos_schema = []  # Inicializar vacío
            rol.save()
            messages.success(request, f"Rol '{rol.nombre}' creado exitosamente.")
            return redirect('dev_gestion_roles')
        else:
            messages.error(request, "Error al crear el rol. Verifica los datos.")
    
    return redirect('dev_gestion_roles')


@login_required
def editar_rol(request, pk):
    """Editar un rol existente"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    rol = get_object_or_404(Rol, pk=pk)
    empresa_activa_id = request.session.get('empresa_activa_id')
    
    if not empresa_activa_id or rol.empresa_id != empresa_activa_id:
        messages.error(request, "No tienes permiso para editar este rol.")
        return redirect('dev_gestion_roles')
    
    if request.method == 'POST':
        form = RolForm(request.POST, instance=rol, empresa=rol.empresa)
        if form.is_valid():
            form.save()
            messages.success(request, f"Rol '{rol.nombre}' actualizado exitosamente.")
            return redirect('dev_gestion_roles')
        else:
            messages.error(request, "Error al actualizar el rol.")
    
    return redirect('dev_gestion_roles')


@login_required
def eliminar_rol(request, pk):
    """Eliminar un rol"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    rol = get_object_or_404(Rol, pk=pk)
    empresa_activa_id = request.session.get('empresa_activa_id')
    
    if not empresa_activa_id or rol.empresa_id != empresa_activa_id:
        messages.error(request, "No tienes permiso para eliminar este rol.")
        return redirect('dev_gestion_roles')
    
    # Verificar que no tenga usuarios asignados
    if rol.usuarios.count() > 0:
        messages.error(request, f"No se puede eliminar el rol '{rol.nombre}' porque tiene {rol.usuarios.count()} usuarios asignados.")
        return redirect('dev_gestion_roles')
    
    if request.method == 'POST':
        nombre_rol = rol.nombre
        rol.delete()
        messages.success(request, f"Rol '{nombre_rol}' eliminado exitosamente.")
        return redirect('dev_gestion_roles')
    
    return redirect('dev_gestion_roles')


@login_required
def toggle_rol_activo(request, pk):
    """Activar/desactivar un rol"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    rol = get_object_or_404(Rol, pk=pk)
    empresa_activa_id = request.session.get('empresa_activa_id')
    
    if not empresa_activa_id or rol.empresa_id != empresa_activa_id:
        messages.error(request, "No tienes permiso para modificar este rol.")
        return redirect('dev_gestion_roles')
    
    rol.activo = not rol.activo
    rol.save()
    estado = "activado" if rol.activo else "desactivado"
    messages.success(request, f"Rol '{rol.nombre}' {estado} exitosamente.")
    
    return redirect('dev_gestion_roles')


@login_required
def agregar_atributo_rol(request, pk):
    """Agregar un atributo al schema del rol"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    rol = get_object_or_404(Rol, pk=pk)
    empresa_activa_id = request.session.get('empresa_activa_id')
    
    if not empresa_activa_id or rol.empresa_id != empresa_activa_id:
        messages.error(request, "No tienes permiso para modificar este rol.")
        return redirect('dev_gestion_roles')
    
    if request.method == 'POST':
        form = AtributoSchemaForm(request.POST)
        if form.is_valid():
            # Construir el nuevo atributo
            nuevo_atributo = {
                'nombre': form.cleaned_data['nombre'],
                'tipo': form.cleaned_data['tipo'],
                'requerido': form.cleaned_data['requerido'],
            }
            
            # Si es tipo selección, agregar las opciones
            if form.cleaned_data['tipo'] == 'seleccion' and form.cleaned_data['opciones']:
                opciones = [op.strip() for op in form.cleaned_data['opciones'].split(',')]
                nuevo_atributo['opciones'] = opciones
            
            # Agregar al schema (inicializar si está vacío)
            if not isinstance(rol.atributos_schema, list):
                rol.atributos_schema = []
            
            rol.atributos_schema.append(nuevo_atributo)
            rol.save()
            
            messages.success(request, f"Atributo '{nuevo_atributo['nombre']}' agregado al rol '{rol.nombre}'.")
            return redirect('dev_gestion_roles')
        else:
            messages.error(request, "Error al agregar el atributo. Verifica los datos.")
    
    return redirect('dev_gestion_roles')


@login_required
def eliminar_atributo_rol(request, pk, atributo_nombre):
    """Eliminar un atributo del schema del rol"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    rol = get_object_or_404(Rol, pk=pk)
    empresa_activa_id = request.session.get('empresa_activa_id')
    
    if not empresa_activa_id or rol.empresa_id != empresa_activa_id:
        messages.error(request, "No tienes permiso para modificar este rol.")
        return redirect('dev_gestion_roles')
    
    if request.method == 'POST':
        # Buscar y eliminar el atributo
        if isinstance(rol.atributos_schema, list):
            rol.atributos_schema = [
                attr for attr in rol.atributos_schema 
                if attr.get('nombre') != atributo_nombre
            ]
            rol.save()
            messages.success(request, f"Atributo '{atributo_nombre}' eliminado del rol '{rol.nombre}'.")
        else:
            messages.error(request, "El rol no tiene atributos definidos.")
        
        return redirect('dev_gestion_roles')
    
    return redirect('dev_gestion_roles')


# ==================== AJUSTES GRÁFICOS ====================

@login_required
def ajustes_graficos(request):
    """Vista para gestionar ajustes gráficos (editar tema de la empresa activa)"""
    if not request.user.is_superuser:
        return redirect('admin_dashboard')
    
    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id:
        messages.warning(request, "Por favor, activa una empresa para poder gestionar sus ajustes gráficos.")
        return redirect('dev_gestion_empresas')
    
    empresa_activa = Empresa.objects.get(id=empresa_activa_id)
    
    # Obtener o crear tema para la empresa
    tema = empresa_activa.tema
    if not tema:
        # Crear tema por defecto si no existe
        tema = Tema.objects.create(
            nombre=f"Tema {empresa_activa.nombre}",
            color_primario='#4CAF50',
            color_secundario='#2196F3',
            color_acento='#FF9800',
            color_texto='#333333',
            color_fondo='#FFFFFF',
            activo=True
        )
        empresa_activa.tema = tema
        empresa_activa.save()
    
    if request.method == 'POST':
        form = TemaForm(request.POST, request.FILES, instance=tema)
        if form.is_valid():
            tema = form.save()
            messages.success(request, "✅ Ajustes gráficos guardados exitosamente.")
            return redirect('dev_ajustes_graficos')
        else:
            messages.error(request, "❌ Error al guardar los ajustes. Verifica los datos.")
    else:
        form = TemaForm(instance=tema)
    
    context = {
        'empresa_activa': empresa_activa,
        'form': form,
        'tema': tema,
    }
    return render(request, 'devpanel/ajustes_graficos.html', context)


# ==================== GESTIÓN DE STAFF (SUPERUSUARIOS) ====================

@login_required
def gestion_staff(request):
    """Vista para gestionar staff (superusuarios) del DevPanel"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect('admin_dashboard')
    
    # Listar solo superusuarios
    superusers = CustomUser.objects.filter(is_superuser=True).order_by('-date_joined')
    
    context = {
        'superusers': superusers,
    }
    return render(request, 'devpanel/gestion_staff.html', context)


@login_required
def crear_staff(request):
    """Crear un nuevo superusuario"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = SuperuserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"✅ Superusuario '{user.username}' creado exitosamente.")
            return redirect('dev_gestion_staff')
        else:
            messages.error(request, "❌ Error al crear el superusuario. Verifica los datos.")
    
    return redirect('dev_gestion_staff')


@login_required
def editar_staff(request, pk):
    """Editar un superusuario existente"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('admin_dashboard')
    
    usuario = get_object_or_404(CustomUser, pk=pk, is_superuser=True)
    
    if request.method == 'POST':
        form = SuperuserEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Superusuario '{usuario.username}' actualizado exitosamente.")
            return redirect('dev_gestion_staff')
        else:
            messages.error(request, "❌ Error al actualizar el superusuario.")
    
    return redirect('dev_gestion_staff')


@login_required
def eliminar_staff(request, pk):
    """Eliminar un superusuario"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('admin_dashboard')
    
    usuario = get_object_or_404(CustomUser, pk=pk, is_superuser=True)
    
    # Evitar que el usuario se elimine a sí mismo
    if usuario.id == request.user.id:
        messages.error(request, "❌ No puedes eliminarte a ti mismo.")
        return redirect('dev_gestion_staff')
    
    # Verificar que haya al menos otro superusuario activo
    otros_superusers = CustomUser.objects.filter(is_superuser=True, is_active=True).exclude(pk=pk).count()
    if otros_superusers == 0:
        messages.error(request, "❌ No puedes eliminar el último superusuario activo del sistema.")
        return redirect('dev_gestion_staff')
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f"✅ Superusuario '{username}' eliminado exitosamente.")
        return redirect('dev_gestion_staff')
    
    return redirect('dev_gestion_staff')


@login_required
def toggle_staff_activo(request, pk):
    """Activar/desactivar un superusuario"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('admin_dashboard')
    
    usuario = get_object_or_404(CustomUser, pk=pk, is_superuser=True)
    
    # Evitar que el usuario se desactive a sí mismo
    if usuario.id == request.user.id:
        messages.error(request, "❌ No puedes desactivarte a ti mismo.")
        return redirect('dev_gestion_staff')
    
    # Si va a desactivar, verificar que haya al menos otro activo
    if usuario.is_active:
        otros_activos = CustomUser.objects.filter(is_superuser=True, is_active=True).exclude(pk=pk).count()
        if otros_activos == 0:
            messages.error(request, "❌ No puedes desactivar el último superusuario activo del sistema.")
            return redirect('dev_gestion_staff')
    
    usuario.is_active = not usuario.is_active
    usuario.save()
    estado = "activado" if usuario.is_active else "desactivado"
    messages.success(request, f"✅ Superusuario '{usuario.username}' {estado} exitosamente.")
    
    return redirect('dev_gestion_staff')


# ==================== GESTIÓN DE MÓDULOS ====================

@login_required
def gestion_modulos(request):
    """Gestionar módulos habilitados para la empresa activa"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect('admin_dashboard')
    
    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id:
        messages.warning(request, "Selecciona una empresa primero.")
        return redirect('dev_gestion_empresas')
    
    empresa = get_object_or_404(Empresa, id=empresa_activa_id)
    
    context = {
        'empresa': empresa,
    }
    return render(request, 'devpanel/gestion_modulos.html', context)


@login_required
def toggle_modulo_productos(request):
    """Activar/desactivar módulo de productos"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('admin_dashboard')
    
    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id:
        messages.warning(request, "Selecciona una empresa primero.")
        return redirect('dev_gestion_empresas')
    
    empresa = get_object_or_404(Empresa, id=empresa_activa_id)
    empresa.productos_habilitado = not empresa.productos_habilitado
    empresa.save()
    
    estado = "habilitado" if empresa.productos_habilitado else "deshabilitado"
    messages.success(request, f"✅ Módulo de Productos {estado} exitosamente.")
    
    return redirect('dev_gestion_modulos')


@login_required
def toggle_modulo_resenas(request):
    """Activar/desactivar módulo de reseñas"""
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('admin_dashboard')
    
    empresa_activa_id = request.session.get('empresa_activa_id')
    if not empresa_activa_id:
        messages.warning(request, "Selecciona una empresa primero.")
        return redirect('dev_gestion_empresas')
    
    empresa = get_object_or_404(Empresa, id=empresa_activa_id)
    empresa.resenas_habilitado = not empresa.resenas_habilitado
    empresa.save()
    
    estado = "habilitado" if empresa.resenas_habilitado else "deshabilitado"
    messages.success(request, f"✅ Módulo de Reseñas {estado} exitosamente.")
    
    return redirect('dev_gestion_modulos')