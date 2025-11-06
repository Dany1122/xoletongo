from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg, Count
from .models import Servicio, TipoServicio, ImagenServicio, Resena
from .forms import ResenaForm
from collections import defaultdict
from django.db.models import Prefetch
from empresas.models import Empresa
from devpanel.models import Pagina, Seccion

# Create your views here.
def detalle_servicio(request, servicio_id):
    # Verificar si el módulo de servicios está habilitado
    empresa = Empresa.objects.filter(activa=True).first()
    if not empresa or not empresa.servicios_habilitado:
        messages.info(request, 'Los servicios no están disponibles en este momento.')
        return redirect('home')
    
    servicio = (
        Servicio.objects
        .select_related('servicio', 'empresa')
        .prefetch_related(
            Prefetch('imagenes', queryset=ImagenServicio.objects.order_by('orden', 'id'))
        )
        .get(pk=servicio_id)
    )
    
    # Verificar si el módulo de reseñas está habilitado
    resenas_habilitado = empresa and empresa.resenas_habilitado
    
    # Inicializar variables de reseñas
    resenas = []
    estadisticas = {'promedio': None, 'total': 0}
    usuario_resena = None
    form = None
    content_type = None
    
    # Solo cargar reseñas si el módulo está habilitado
    if resenas_habilitado:
        # Obtener ContentType de Servicio
        content_type = ContentType.objects.get_for_model(Servicio)
        
        # Obtener reseñas aprobadas
        resenas = Resena.objects.filter(
            content_type=content_type,
            object_id=servicio_id,
            aprobada=True
        ).select_related('usuario').order_by('-fecha_creacion')
        
        # Calcular promedio de calificaciones
        estadisticas = resenas.aggregate(
            promedio=Avg('calificacion'),
            total=Count('id')
        )
        
        # Verificar si el usuario ya dejó una reseña
        if request.user.is_authenticated:
            usuario_resena = resenas.filter(usuario=request.user).first()
        
        # Crear formulario para nueva reseña
        form = ResenaForm()
    
    return render(request, 'servicio.html', {
        'servicio': servicio,
        'opacidad': 0.4,
        'resenas': resenas,
        'estadisticas_resenas': estadisticas,
        'usuario_resena': usuario_resena,
        'form_resena': form,
        'content_type': content_type,
        'resenas_habilitado': resenas_habilitado,
    })

def servicios_por_tipo(request):
    """
    Vista dinámica para la página de servicios.
    Carga las secciones desde la BD y también pasa los tipos de servicio.
    """
    # Obtener empresa activa
    empresa = Empresa.objects.filter(activa=True).first()
    
    # Verificar si el módulo de servicios está habilitado
    if not empresa or not empresa.servicios_habilitado:
        messages.info(request, 'Los servicios no están disponibles en este momento.')
        return redirect('home')
    
    # Obtener servicios y tipos (OBLIGATORIO para la funcionalidad)
    servicios_qs = (
        Servicio.objects
        .select_related('servicio', 'empresa')
        .prefetch_related(
            Prefetch('imagenes', queryset=ImagenServicio.objects.order_by('orden', 'id'))
        )
        .order_by('titulo')
    )

    tipos_servicio = (
        TipoServicio.objects
        .order_by('nombre')
        .prefetch_related(
            Prefetch('subservicios', queryset=servicios_qs)
        )
    )
    
    # Obtener secciones dinámicas
    secciones = []
    if empresa:
        try:
            pagina = Pagina.objects.get(empresa=empresa, slug='servicios')
            secciones = Seccion.objects.filter(pagina=pagina, activa=True).order_by('orden')
        except Pagina.DoesNotExist:
            pass
    
    return render(request, 'servicios_por_tipo.html', {
        'tipos_servicio': tipos_servicio,
        'secciones': secciones,
        'empresa': empresa
    })


@login_required
def crear_resena(request, content_type_id, object_id):
    """Vista genérica para crear reseñas de servicios o productos"""
    # Verificar si el módulo de reseñas está habilitado
    empresa = Empresa.objects.filter(activa=True).first()
    if not empresa or not empresa.resenas_habilitado:
        messages.error(request, 'El sistema de reseñas no está disponible en este momento.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    if request.method == 'POST':
        content_type = get_object_or_404(ContentType, id=content_type_id)
        objeto = content_type.get_object_for_this_type(id=object_id)
        
        # Verificar si el usuario ya tiene una reseña
        resena_existente = Resena.objects.filter(
            usuario=request.user,
            content_type=content_type,
            object_id=object_id
        ).first()
        
        if resena_existente:
            messages.warning(request, 'Ya has dejado una reseña para este elemento.')
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        
        form = ResenaForm(request.POST)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.usuario = request.user
            resena.content_type = content_type
            resena.object_id = object_id
            resena.save()
            messages.success(request, '¡Gracias por tu reseña!')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
        
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    return redirect('home')


@login_required
def editar_resena(request, resena_id):
    """Vista para editar una reseña existente"""
    # Verificar si el módulo de reseñas está habilitado
    empresa = Empresa.objects.filter(activa=True).first()
    if not empresa or not empresa.resenas_habilitado:
        messages.error(request, 'El sistema de reseñas no está disponible en este momento.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    resena = get_object_or_404(Resena, id=resena_id)
    
    # Verificar permisos: el autor o usuarios con roles de staff pueden editar
    rol_usuario = request.user.get_rol_nombre()
    puede_editar = (
        request.user == resena.usuario or 
        rol_usuario in ['Administrador', 'Empleado', 'Encargado']
    )
    
    if not puede_editar:
        messages.error(request, 'No tienes permiso para editar esta reseña.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    if request.method == 'POST':
        form = ResenaForm(request.POST, instance=resena)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reseña actualizada exitosamente.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
        
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    return redirect('home')


@login_required
def eliminar_resena(request, resena_id):
    """Vista para eliminar una reseña"""
    # Verificar si el módulo de reseñas está habilitado
    empresa = Empresa.objects.filter(activa=True).first()
    if not empresa or not empresa.resenas_habilitado:
        messages.error(request, 'El sistema de reseñas no está disponible en este momento.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    resena = get_object_or_404(Resena, id=resena_id)
    
    # Verificar permisos: el autor o usuarios con roles de staff pueden eliminar
    rol_usuario = request.user.get_rol_nombre()
    puede_eliminar = (
        request.user == resena.usuario or 
        rol_usuario in ['Administrador', 'Empleado', 'Encargado']
    )
    
    if not puede_eliminar:
        messages.error(request, 'No tienes permiso para eliminar esta reseña.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    if request.method == 'POST':
        resena.delete()
        messages.success(request, 'Reseña eliminada exitosamente.')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))