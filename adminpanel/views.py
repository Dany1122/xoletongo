from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from usuarios.models import CustomUser
from reservaciones.models import Reservacion
from empresas.models import Empresa
from adminpanel.forms import CustomUserForm, CustomUserEditForm
from django.core.paginator import Paginator
from django.db.models import Q
from collections import defaultdict
from .models import Venta

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
    pendientes = Venta.objects.filter(estado='Pendiente').order_by('-fecha')
    pagadas = Venta.objects.filter(estado='Pagado').order_by('-fecha')
    canceladas = Venta.objects.filter(estado='Cancelado').order_by('-fecha')


    context = {
        'pendientes': pendientes,
        'pagadas': pagadas,
        'canceladas': canceladas,
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