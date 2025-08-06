from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from usuarios.models import CustomUser
from servicios.models import Servicio, TipoServicio
from reservaciones.models import Reservacion, Reservacion_servicio
from empresas.models import Empresa
from adminpanel.forms import CustomUserForm, ServicioForm, CustomUserEditForm
from django.core.paginator import Paginator
from django.db.models import Q
from collections import defaultdict
from django.contrib import messages
from .models import Venta
from itertools import chain
from django.db.models import Sum,Count
from datetime import datetime
from adminpanel.utils import registrar_novedad
from adminpanel.models import Novedad


from django.core.paginator import Paginator
from django.db.models import Q
from collections import defaultdict
# ── PDF ─────────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.http import FileResponse
import io

@login_required
def dashboard(request):
    empresa = Empresa.objects.filter(activa=True).first()
    total_usuarios = CustomUser.objects.count()
    total_reservaciones = Reservacion.objects.count()
    total_servicios = Servicio.objects.count()
    total_ventas = Venta.objects.aggregate(total=Sum('monto'))['total'] or 0
    clientes_activos = CustomUser.objects.filter(is_active=True).count()
    ultimo_ingreso = request.user.last_login

    # Servicio más solicitado
    servicio_popular = (
        Reservacion_servicio.objects
        .values('servicio__titulo')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )
    servicio_mas_solicitado = servicio_popular['servicio__titulo'] if servicio_popular else 'Sin datos'

    # Reservaciones pendientes
    reservaciones_pendientes = Reservacion.objects.filter(estado='pendiente').count()

     # Novedades recientes
    novedades = Novedad.objects.order_by('-fecha')[:10]

    return render(request, 'dashboard.html', {
        'empresa': empresa,
        'total_usuarios': total_usuarios,
        'total_reservaciones': total_reservaciones,
        'total_servicios': total_servicios,
        'total_ventas': total_ventas,
        'clientes_activos': clientes_activos,
        'ultimo_ingreso': ultimo_ingreso,
        'servicio_mas_solicitado': servicio_mas_solicitado,
        'reservaciones_pendientes': reservaciones_pendientes,
        'novedades': novedades,
    })


def lista_usuarios(request):
    # ── Búsqueda ────────────────────────────────────────────────────────────────
    q = request.GET.get("q", "").strip()
    queryset = CustomUser.objects.all()

    if q:
        queryset = queryset.filter(
            Q(username__icontains=q) |
            Q(email__icontains=q) |
            Q(nombre_completo__icontains=q) |
            Q(rol__icontains=q)
        )

    queryset = queryset.order_by('-id')  # ordenar por más reciente

    # ── Agrupar manualmente últimos 4 por rol ───────────────────────────────────
    grupos_ultimos = defaultdict(list)
    for user in queryset:
        if len(grupos_ultimos[user.rol]) < 4:
            grupos_ultimos[user.rol].append(user)

    grupos_por_rol = [
        {"rol": rol, "usuarios": grupos_ultimos[rol]}
        for rol in grupos_ultimos
    ]

    # ── Paginación de la tabla completa ─────────────────────────────────────────
    paginator = Paginator(queryset, 10)  # 10 por página
    page_num = request.GET.get("page")
    page_obj = paginator.get_page(page_num)

    return render(request, "lista_usuarios.html", {
        "grupos_por_rol": grupos_por_rol,
        "page_obj": page_obj,
        "q": q,
    })

def editar_usuario(request, id):
    usuario = get_object_or_404(CustomUser, id=id)
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            registrar_novedad(request.user, f"Editó el usuario: {usuario.username}")
            return redirect('/adminpanel/usuarios/?editado=1')
    else:
        form = CustomUserEditForm(instance=usuario)
    return render(request, 'editar_usuario.html', {'form': form})

def eliminar_usuario(request, id):
    usuario = get_object_or_404(CustomUser, id=id)
    usuario.delete()
    registrar_novedad(request.user, f"Eliminó al usuario: {usuario.username}")
    return redirect('/adminpanel/usuarios/?eliminado=1')

def agregar_usuario(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            usuario=form.save()
            registrar_novedad(request.user, f"Agregó un usuario: {usuario.username}")
            return redirect('/adminpanel/usuarios/?creado=1')
    else:
        form = CustomUserForm()
    return render(request, 'agregar_usuario.html', {'form': form})

def kanban_ventas(request):
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    busqueda = request.GET.get("busqueda", "").strip()

    filtros = Q()
    if fecha_inicio:
        filtros &= Q(fecha_reserva__date__gte=fecha_inicio)
    if fecha_fin:
        filtros &= Q(fecha_reserva__date__lte=fecha_fin)
    if busqueda:
        filtros &= (
            Q(nombre_cliente__icontains=busqueda) |
            Q(email_cliente__icontains=busqueda) |
            Q(id__icontains=busqueda)
        )

    # Filtrar todas según los filtros generales
    todas_filtradas = Reservacion.objects.filter(filtros).order_by('-fecha_reserva')

    total_registros = todas_filtradas.count()

    # Filtrar para columnas del Kanban (últimos 5 de cada estado)
    pendientes = todas_filtradas.filter(estado='pendiente')[:5]
    pagados = todas_filtradas.filter(estado='aprobada')[:5]
    cancelados = todas_filtradas.filter(estado='finalizada')[:5]

    # Totales por estado (con los mismos filtros aplicados)
    total_pendientes = todas_filtradas.filter(estado='pendiente').aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0
    total_pagados = todas_filtradas.filter(estado='aprobada').aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0
    total_cancelados = todas_filtradas.filter(estado='finalizada').aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0

    # Paginación de la lista general
    paginator = Paginator(todas_filtradas, 10)  # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Agregar filtros rápidos al contexto
    from datetime import date, timedelta
    hoy = date.today()
    semana_inicio = hoy - timedelta(days=hoy.weekday())
    mes_inicio = hoy.replace(day=1)

    context = {
        'pendientes': pendientes,
        'pagados': pagados,
        'cancelados': cancelados,
        'todas': todas_filtradas,
        'page_obj': page_obj,
        'total_pendientes': total_pendientes,
        'total_pagados': total_pagados,
        'total_cancelados': total_cancelados,
        'total_registros': total_registros,
    }

    context.update({
        'hoy': hoy.isoformat(),
        'semana_inicio': semana_inicio.isoformat(),
        'mes_inicio': mes_inicio.isoformat(),
    })
    return render(request, 'kanban_ventas.html', context)


@login_required
def exportar_usuarios_pdf(request):
    # — 1.  Obtener todos los usuarios (aplica aquí cualquier filtro si hace falta)
    usuarios = CustomUser.objects.all().order_by("rol", "username")

    # — 2.  Crear un buffer en memoria
    buffer = io.BytesIO()
    pdf     = canvas.Canvas(buffer, pagesize=LETTER)

    width, height = LETTER
    y = height - 50                               # margen superior

    # — 3.  Encabezado
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "Listado de usuarios – Xoletongo")
    y -= 30

    # — 4.  Columnas
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(colors.HexColor("#1a73e8"))
    pdf.drawString(40, y, "Usuario")
    pdf.drawString(200, y, "Email")
    pdf.drawString(400, y, "Rol")
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica", 10)
    y -= 15
    pdf.line(40, y, width - 40, y)
    y -= 20

    # — 5.  Filas
    for u in usuarios:
        if y < 60:                                # salto de página
            pdf.showPage()
            y = height - 50
        pdf.drawString(40,  y, u.username)
        pdf.drawString(200, y, u.email or "—")
        pdf.drawString(400, y, u.rol)
        y -= 18

    # — 6.  Cerrar el PDF
    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    registrar_novedad(request.user, "Exportó PDF con listado de usuarios")

    return FileResponse(buffer,
                        as_attachment=True,
                        filename="usuarios_xoletongo.pdf")

def lista_servicios(request):
    empresa = Empresa.objects.filter(activa=True).first()
    if not empresa:
        return render(request, 'lista_servicios.html', {'error': 'No hay empresa activa'})

    q = request.GET.get("q", "").strip()
    queryset = Servicio.objects.filter(empresa=empresa)
    if q:
        queryset = queryset.filter(
            Q(titulo__icontains=q) | Q(descripcion__icontains=q)
        )

    queryset = queryset.order_by('-id')

    # Agrupar los últimos 4 por tipo
    agrupados = defaultdict(list)
    for servicio in queryset:
        if len(agrupados[servicio.servicio]) < 4:
            agrupados[servicio.servicio].append(servicio)

    servicios_por_tipo = [
        {"tipo": tipo, "servicios": agrupados[tipo]}
        for tipo in agrupados
    ]

    # Paginación
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'lista_servicios.html', {
        "empresa": empresa,
        "servicios_por_tipo": servicios_por_tipo,
        "page_obj": page_obj,
        "q": q
    })

def agregar_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            servicio = form.save()
            registrar_novedad(request.user, f"Agregó un servicio: {servicio.titulo}")
            return redirect('/adminpanel/servicios/?creado=1')
    else:
        form = ServicioForm()
    return render(request, 'agregar_servicio.html', {'form': form})

def editar_servicio(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            registrar_novedad(request.user, f"Editó el servicio: {servicio.titulo}")
            return redirect('/adminpanel/servicios/?editado=1')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'editar_servicio.html', {'form': form})

def eliminar_servicio(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    registrar_novedad(request.user, f"Eliminó el servicio: {servicio.titulo}")
    servicio.delete()
    return redirect('/adminpanel/servicios/?eliminado=1')

def exportar_servicios_pdf(request):

    return 0

def lista_reservaciones(request):
    if request.method == 'POST':
        reservacion_id = request.POST.get('reservacion_id')
        nuevo_estado = request.POST.get('estado')
        reservacion = get_object_or_404(Reservacion, id=reservacion_id)
        reservacion.estado = nuevo_estado
        reservacion.save()
        registrar_novedad(request.user, f"Actualizó estado de reservación #{reservacion.id} a {nuevo_estado}")
        return redirect('admin_reservaciones')

    reservaciones = Reservacion.objects.all().order_by('-fecha_reserva')
    reservaciones_con_servicio = []

    for r in reservaciones:
        servicio = None
        relacion = Reservacion_servicio.objects.filter(id_reservacion=r).first()
        if relacion:
            servicio = relacion.servicio
        reservaciones_con_servicio.append({
            'reservacion': r,
            'servicio': servicio,
            'tipo_servicio': servicio.servicio.tipo if servicio else None,
            'titulo_servicio': servicio.titulo if servicio else 'Sin servicio',
            'total_pagado': r.total_pagado,
        })

    return render(request, 'lista_reservaciones.html', {
        'reservaciones': reservaciones_con_servicio
    })

@login_required
def exportar_ventas_pdf(request):
    # Reaplicar filtros para exportar el mismo conjunto de datos
    fecha_inicio = request.GET.get("fecha_inicio")
    fecha_fin = request.GET.get("fecha_fin")
    busqueda = request.GET.get("busqueda", "").strip()

    filtros = Q()
    if fecha_inicio:
        filtros &= Q(fecha_reserva__date__gte=fecha_inicio)
    if fecha_fin:
        filtros &= Q(fecha_reserva__date__lte=fecha_fin)
    if busqueda:
        filtros &= (
            Q(nombre_cliente__icontains=busqueda) |
            Q(email_cliente__icontains=busqueda) |
            Q(id__icontains=busqueda)
        )

    queryset = Reservacion.objects.filter(filtros).order_by('-fecha_reserva')

    total_registros = queryset.count()
    total_pendientes = queryset.filter(estado='pendiente').aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0
    total_pagados = queryset.filter(estado='aprobada').aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0
    total_cancelados = queryset.filter(estado='finalizada').aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0

    # Crear PDF
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "Resumen de Ventas – Xoletongo")
    y -= 30

    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, y, f"Total de registros: {total_registros}")
    y -= 20
    pdf.drawString(40, y, f"Total Pendientes: ${total_pendientes}")
    y -= 20
    pdf.drawString(40, y, f"Total Pagados: ${total_pagados}")
    y -= 20
    pdf.drawString(40, y, f"Total Cancelados: ${total_cancelados}")
    y -= 30

    # Encabezado de tabla
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, y, "ID")
    pdf.drawString(80, y, "Cliente")
    pdf.drawString(200, y, "Email")
    pdf.drawString(360, y, "Estado")
    pdf.drawString(440, y, "Monto")
    y -= 15
    pdf.line(40, y, width - 40, y)
    y -= 10

    # Filas de tabla
    pdf.setFont("Helvetica", 9)
    for r in queryset:
        if y < 60:
            pdf.showPage()
            y = height - 50
        pdf.drawString(40, y, str(r.id))
        pdf.drawString(80, y, r.nombre_cliente[:18])
        pdf.drawString(200, y, r.email_cliente[:25])
        pdf.drawString(360, y, r.estado.capitalize())
        pdf.drawString(440, y, f"${r.total_pagado}")
        y -= 14

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    registrar_novedad(request.user, "Exportó PDF con resumen de ventas")

    return FileResponse(buffer, as_attachment=True, filename="resumen_ventas.pdf")




