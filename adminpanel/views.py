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
from django.db.models import Sum

# ── PDF ─────────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.http import FileResponse
import io

def dashboard(request):
    empresa = Empresa.objects.filter(activa=True).first()
    total_usuarios = CustomUser.objects.count()
    total_reservaciones = Reservacion.objects.count()
    return render(request, 'dashboard.html', {
        'empresa': empresa,
        'total_usuarios': total_usuarios,
        'total_reservaciones': total_reservaciones,
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
            return redirect('/adminpanel/usuarios/?editado=1')
    else:
        form = CustomUserEditForm(instance=usuario)
    return render(request, 'editar_usuario.html', {'form': form})

def eliminar_usuario(request, id):
    usuario = get_object_or_404(CustomUser, id=id)
    usuario.delete()
    return redirect('/adminpanel/usuarios/?eliminado=1')

def agregar_usuario(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/adminpanel/usuarios/?creado=1')
    else:
        form = CustomUserForm()
    return render(request, 'agregar_usuario.html', {'form': form})

def kanban_ventas(request):
    pendientes = Reservacion.objects.filter(estado='pendiente').order_by('-fecha_reserva')[:5]
    pagados = Reservacion.objects.filter(estado='aprobada').order_by('-fecha_reserva')[:5]
    cancelados = Reservacion.objects.filter(estado='finalizada').order_by('-fecha_reserva')[:5]

    # Totales por estado
    total_pendientes = Reservacion.objects.filter(estado='pendiente').aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0
    total_pagados = Reservacion.objects.filter(estado='aprobada').aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0
    total_cancelados = Reservacion.objects.filter(estado='finalizada').aggregate(Sum('total_pagado'))['total_pagado__sum'] or 0

    todas = list(chain(
        Reservacion.objects.filter(estado='pendiente'),
        Reservacion.objects.filter(estado='aprobada'),
        Reservacion.objects.filter(estado='finalizada')
    ))

    context = {
        'pendientes': pendientes,
        'pagados': pagados,
        'cancelados': cancelados,
        'todas': todas,
        'total_pendientes': total_pendientes,
        'total_pagados': total_pagados,
        'total_cancelados': total_cancelados,
    }
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
            form.save()
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
            return redirect('/adminpanel/servicios/?editado=1')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'editar_servicio.html', {'form': form})

def eliminar_servicio(id):
    servicio = get_object_or_404(Servicio, id=id)
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