from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from usuarios.models import CustomUser
from servicios.models import Servicio, TipoServicio
from reservaciones.models import Reservacion, Reservacion_servicio
from empresas.models import Empresa
from adminpanel.forms import CustomUserForm, ServicioForm, CustomUserEditForm, EmpresaForm, ProductoForm, CategoriaProductoForm, TipoServicioForm, ImagenFormSet 
from django.core.paginator import Paginator
from django.db.models import Q
from collections import defaultdict
from django.contrib import messages
from .models import Venta
from itertools import chain
from django.db.models import Sum,Count
from datetime import datetime
from adminpanel.utils import registrar_novedad
from adminpanel.models import Novedad, Producto, CategoriaProducto, Pedido, ItemPedido
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from decimal import Decimal
from django.db import transaction



from django.core.paginator import Paginator
from django.db.models import Q
from collections import defaultdict
# ── PDF ─────────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
import io

def _user_is_admin(user):
    return (
        getattr(user, "is_superuser", False)
        or user.groups.filter(name__iexact="administrador").exists()
        or getattr(user, "rol", "").lower() == "administrador"
    )

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
    empresa_activa = Empresa.objects.filter(activa=True).first()
    
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=usuario, empresa=empresa_activa)
        if form.is_valid():
            form.save()
            registrar_novedad(request.user, f"Editó el usuario: {usuario.username}")
            return redirect('/adminpanel/usuarios/?editado=1')
    else:
        form = CustomUserEditForm(instance=usuario, empresa=empresa_activa)
    return render(request, 'editar_usuario.html', {'form': form})

def eliminar_usuario(request, id):
    usuario = get_object_or_404(CustomUser, id=id)
    usuario.delete()
    registrar_novedad(request.user, f"Eliminó al usuario: {usuario.username}")
    return redirect('/adminpanel/usuarios/?eliminado=1')

def agregar_usuario(request):
    empresa_activa = Empresa.objects.filter(activa=True).first()
    
    if request.method == 'POST':
        form = CustomUserForm(request.POST, empresa=empresa_activa)
        if form.is_valid():
            usuario = form.save(commit=False)
            if empresa_activa:
                usuario.empresa = empresa_activa
            usuario.save()
            registrar_novedad(request.user, f"Agregó un usuario: {usuario.username}")
            return redirect('/adminpanel/usuarios/?creado=1')
    else:
        form = CustomUserForm(empresa=empresa_activa)
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
    # Obtenemos la empresa activa
    empresa_activa = Empresa.objects.filter(activa=True).first()
    if not empresa_activa:
        messages.error(request, "No hay una empresa activa configurada.")
        form = ServicioForm(request.POST or None, request.FILES or None, empresa=None)
        formset = ImagenFormSet(request.POST or None, request.FILES or None)
        return render(request, 'agregar_servicio.html', {'form': form, 'formset': formset})

    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, empresa=empresa_activa)
        formset = ImagenFormSet(request.POST, request.FILES)  # sin instance hasta guardar el servicio

        if form.is_valid():
            with transaction.atomic():
                servicio = form.save(commit=False)
                servicio.empresa = empresa_activa            # ✅ empresa activa
                servicio.save()

                # Ligamos la galería al servicio recién creado
                formset = ImagenFormSet(request.POST, request.FILES, instance=servicio)
                if formset.is_valid():
                    formset.save()
                    registrar_novedad(request.user, f"Agregó un servicio: {servicio.titulo}")
                    return redirect('/adminpanel/servicios/?creado=1')
                else:
                    # ❗ Si la galería falla, borra el servicio y rearmar formset sin instance
                    servicio.delete()
                    messages.error(request, "Revisa los campos de la galería.")
                    formset = ImagenFormSet(request.POST, request.FILES)  # ← agregado
            # si el formset NO es válido, seguimos a render con errores
        # si el form NO es válido, caemos a render con errores
    else:
        form = ServicioForm(empresa=empresa_activa)
        formset = ImagenFormSet()

    return render(request, 'agregar_servicio.html', {'form': form, 'formset': formset})

def editar_servicio(request, id):
    servicio = get_object_or_404(Servicio, id=id)

    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES, instance=servicio, empresa=servicio.empresa)
        formset = ImagenFormSet(request.POST, request.FILES, instance=servicio)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # No cambiamos la empresa aquí; el servicio ya la tiene
                form.save()
                formset.save()
                registrar_novedad(request.user, f"Editó el servicio: {servicio.titulo}")
            return redirect('/adminpanel/servicios/?editado=1')
    else:
        form = ServicioForm(instance=servicio, empresa=servicio.empresa)
        formset = ImagenFormSet(instance=servicio)

    return render(request, 'editar_servicio.html', {'form': form, 'formset': formset, 'servicio': servicio})

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

def exportar_reservas_pdf(request):
    # Ejemplo mínimo: PDF vacío (header correcto)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="reservas.pdf"'
    # Contenido PDF real: usa ReportLab/WeasyPrint más adelante
    response.write(b"%PDF-1.4\n%...\n")  # placeholder
    return response

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


@login_required
def configuracion_empresa(request):
    # Si manejas única empresa activa
    empresa = Empresa.objects.filter(activa=True).first()
    is_admin = _user_is_admin(request.user)

    if request.method == "POST":
        if not is_admin:
            return HttpResponseForbidden("No tienes permisos para modificar la configuración de la empresa.")
        form = EmpresaForm(request.POST, request.FILES, instance=empresa)
        if form.is_valid():
            was_created = empresa is None
            empresa = form.save()
            flag = "creado=1" if was_created else "editado=1"
            # ⬇️ usa el nombre correcto de la ruta
            return redirect(f"{reverse('configuracion_empresa')}?{flag}")
    else:
        form = EmpresaForm(instance=empresa)
        if not is_admin:
            for f in form.fields.values():
                f.disabled = True

    return render(
        request,
        "confEmpresa.html",  # si tu template se llama así, déjalo igual
        {"form": form, "is_admin": is_admin, "empresa": empresa},
    )

def admin_productos(request):
    # --- La lógica de filtrado y búsqueda se mantiene igual ---
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', None)

    productos_list = Producto.objects.all().order_by('-creado_en') # Ordenamos por fecha de creación

    if query:
        productos_list = productos_list.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(sku__icontains=query)
        )
    if categoria_id:
        productos_list = productos_list.filter(categoria__id=categoria_id)

    # --- Lógica de Paginación para la tabla principal ---
    paginator = Paginator(productos_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # --- ✨ NUEVO: Obtener los últimos 10 productos para la galería ---
    ultimos_productos = Producto.objects.all().order_by('-creado_en')[:10]

    categorias = CategoriaProducto.objects.all()

    context = {
        'page_obj': page_obj,                          # Para la tabla paginada
        'ultimos_productos': ultimos_productos,        # ¡NUEVA VARIABLE para la galería!
        'categorias': categorias,
        'query_actual': query,
        'categoria_actual_id': int(categoria_id) if categoria_id else None,
    }
    return render(request, 'lista_productos.html', context)


@login_required
def admin_agregar_producto(request):
    empresa_usuario = request.user.empresa # Obtenemos la empresa
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, empresa=empresa_usuario)
        if form.is_valid():
            # El nuevo método save() del formulario se encargará de todo
            form.save()
            return redirect('admin_productos')
    else:
        form = ProductoForm(empresa=empresa_usuario)
    return render(request, 'agregar_producto.html', {'form': form})

def crear_categoria_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        if nombre:
            CategoriaProducto.objects.create(nombre=nombre, descripcion=descripcion)
    return redirect('admin_productos')

@login_required
def editar_producto(request, pk):
    empresa_usuario = request.user.empresa
    producto = get_object_or_404(Producto, pk=pk, empresa=empresa_usuario)
    if request.method == 'POST':
        # 👇 Pasamos la empresa al formulario
        form = ProductoForm(request.POST, request.FILES, instance=producto, empresa=empresa_usuario)
        if form.is_valid():
            form.save()
            return redirect('admin_productos')
    else:
        # 👇 Pasamos la empresa también aquí
        form = ProductoForm(instance=producto, empresa=empresa_usuario)
    return render(request, 'editar_producto.html', {'form': form, 'producto': producto})


@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        registrar_novedad(request.user, f"Eliminó el producto: {nombre_producto}")
        return redirect('admin_productos')
    
    return render(request, 'eliminar_producto_confirmar.html', {'producto': producto})

def lista_categorias(request):
    """
    Vista para listar, crear, editar y eliminar categorías.
    """
    categorias = CategoriaProducto.objects.all().order_by('nombre')
    context = {
        'categorias': categorias
    }
    return render(request, 'lista_categorias.html', context)

@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(CategoriaProducto, pk=pk)
    # Esta vista ahora solo necesita manejar peticiones POST del modal
    if request.method == 'POST':
        form = CategoriaProductoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('admin_categorias')
    # Si alguien intenta acceder por GET, simplemente lo regresamos
    return redirect('admin_categorias')

@login_required
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(CategoriaProducto, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        return redirect('admin_categorias')
    # Si no es POST, redirigir por seguridad (la confirmación se hace en el modal)
    return redirect('admin_categorias')


@login_required
def exportar_productos_pdf(request):
    # 1. Replicar la lógica de filtrado de la vista principal
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', None)

    productos = Producto.objects.all().order_by('nombre') # Ordenamos por nombre para el reporte

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(sku__icontains=query)
        )
    if categoria_id:
        productos = productos.filter(categoria__id=categoria_id)

    # 2. Crear el buffer de memoria para el PDF
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # 3. Escribir el contenido del PDF
    y = height - 50 # Margen superior

    # Título
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "Listado de Productos")
    y -= 30

    # Encabezados de la tabla
    pdf.setFont("Helvetica-Bold", 10)
    columnas = ["Nombre", "SKU", "Precio", "Stock", "Categoría"]
    x_pos = [40, 250, 320, 380, 440] # Posiciones X para cada columna
    
    for i, columna in enumerate(columnas):
        pdf.drawString(x_pos[i], y, columna)
    
    y -= 15
    pdf.line(40, y, width - 40, y) # Línea separadora
    y -= 15
    
    # Filas de datos
    pdf.setFont("Helvetica", 9)
    for producto in productos:
        # Salto de página si llegamos al final
        if y < 60:
            pdf.showPage()
            pdf.setFont("Helvetica", 9)
            y = height - 50

        pdf.drawString(x_pos[0], y, producto.nombre[:40]) # Acortamos el nombre si es muy largo
        pdf.drawString(x_pos[1], y, producto.sku or "-")
        pdf.drawString(x_pos[2], y, f"${producto.precio}")
        pdf.drawString(x_pos[3], y, str(producto.stock))
        pdf.drawString(x_pos[4], y, producto.categoria.nombre if producto.categoria else "Sin categoría")
        
        y -= 18

    # 4. Finalizar y guardar el PDF
    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    # 5. Devolver el archivo como una descarga
    return FileResponse(buffer, as_attachment=True, filename="listado_de_productos.pdf")


def admin_reservaciones(request):
    """
    Lista de reservaciones con filtros GET y paginación,
    mapeando tus nombres reales de campos:
      - Reservacion_servicio.id_reservacion -> Reservacion
      - Servicio.servicio.tipo -> 'porHora' | 'porDia'
    """
    q = (request.GET.get("q") or "").strip()
    tipo = (request.GET.get("tipo") or "").strip()  # 'porHora' | 'porDia' | ''
    page = request.GET.get("page")

    # select_related con los NOMBRES DE CAMPO reales (no related_name del reverso)
    rs_qs = (
        Reservacion_servicio.objects
        .select_related("id_reservacion", "servicio", "servicio__servicio")
        .order_by("-id")
    )

    # Filtro por texto (cliente o email) usando el nombre DEL CAMPO FK: id_reservacion
    if q:
        rs_qs = rs_qs.filter(
            Q(id_reservacion__nombre_cliente__icontains=q) |
            Q(id_reservacion__email_cliente__icontains=q)
        )

    # Filtro por tipo de servicio: Servicio.servicio.tipo (FK a TipoServicio con campo 'tipo')
    if tipo in ("porHora", "porDia"):
        rs_qs = rs_qs.filter(servicio__servicio__tipo=tipo)

    # Armar items consumibles por el template
    items = []
    for rs in rs_qs:
        r = rs.id_reservacion     # <- ojo: tu FK se llama id_reservacion
        s = rs.servicio
        ts = getattr(s, "servicio", None)  # FK a TipoServicio (mal-nombrado pero así está)
        tipo_servicio = getattr(ts, "tipo", None) or "no"

        total_pagado = getattr(r, "total_pagado", Decimal("0.00"))
        pago_realizado = bool(getattr(r, "pago_realizado", False))

        items.append({
            "reservacion": r,
            "servicio": s,
            "tipo_servicio": tipo_servicio,                   # 'porHora'/'porDia'/'no'
            "titulo_servicio": getattr(s, "titulo", "Servicio"),
            "total_pagado": total_pagado,
            "pago_realizado": pago_realizado,
        })

    paginator = Paginator(items, 12)
    page_obj = paginator.get_page(page)

    context = {
        "page_obj": page_obj,
        "query_actual": q,
        "tipo_actual": tipo,
        "ESTADOS_GLOBALES": Reservacion.ESTADOS,  # ('pendiente','aprobada','finalizada')
    }
    return render(request, "lista_reservaciones.html", context)


# ---------- ACTUALIZAR ESTADO (desde modal) ----------
def admin_actualizar_estado_reservacion(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    reservacion_id = request.POST.get("reservacion_id")
    estado = request.POST.get("estado")

    if not reservacion_id or not estado:
        messages.error(request, "Faltan datos para actualizar el estado.")
        return redirect(_rebuild_list_url(request))

    reservacion = get_object_or_404(Reservacion, pk=reservacion_id)

    estados_validos = {k for k, _ in Reservacion.ESTADOS}
    if estado not in estados_validos:
        messages.error(request, "Estado inválido.")
        return redirect(_rebuild_list_url(request))

    reservacion.estado = estado
    reservacion.save(update_fields=["estado"])
    messages.success(
        request,
        f"Reservación #{reservacion.id} actualizada a '{reservacion.get_estado_display()}'."
    )
    return redirect(_rebuild_list_url(request))


# ---------- EXPORTAR PDF (stub en TXT para probar) ----------
def admin_exportar_reservas_pdf(request):
    q = (request.GET.get("q") or "").strip()
    tipo = (request.GET.get("tipo") or "").strip()

    rs_qs = (
        Reservacion_servicio.objects
        .select_related("id_reservacion", "servicio", "servicio__servicio")
        .order_by("-id")
    )

    if q:
        rs_qs = rs_qs.filter(
            Q(id_reservacion__nombre_cliente__icontains=q) |
            Q(id_reservacion__email_cliente__icontains=q)
        )
    if tipo in ("porHora", "porDia"):
        rs_qs = rs_qs.filter(servicio__servicio__tipo=tipo)

    lines = [f"Listado de reservaciones (q='{q}', tipo='{tipo}')\n"]
    for rs in rs_qs[:200]:
        r = rs.id_reservacion
        s = rs.servicio
        lines.append(f"- #{r.id} {r.nombre_cliente} / {getattr(s, 'titulo', 'Servicio')}")

    content = "\n".join(lines)
    response = HttpResponse(content, content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="reservas.txt"'
    return response


# ---------- util ----------
def _rebuild_list_url(request):
    base = reverse("admin_reservaciones")
    q = request.GET.get("q", "")
    tipo = request.GET.get("tipo", "")
    page = request.GET.get("page", "")
    params = []
    if q:
        params.append(f"q={q}")
    if tipo:
        params.append(f"tipo={tipo}")
    if page:
        params.append(f"page={page}")
    return base + (("?" + "&".join(params)) if params else "")


# Página de gestión (lista, crear rápido, links a editar/eliminar)
@login_required
def admin_tipos_servicio(request):
    # Obtener empresa activa y filtrar tipos de servicio
    empresa_activa = Empresa.objects.filter(activa=True).first()
    
    if empresa_activa:
        tipos = TipoServicio.objects.filter(empresa=empresa_activa).annotate(num_servicios=Count("subservicios"))
        form = TipoServicioForm(empresa=empresa_activa)
    else:
        tipos = TipoServicio.objects.none()
        form = TipoServicioForm()
        messages.warning(request, "No hay una empresa activa configurada.")
    
    return render(request, "admin_tipos_servicio.html", {
        "tipos": tipos,
        "form": form,
    })

# Crear desde el modal (y redirige a donde estabas)
@login_required
def crear_tipo_servicio(request):
    if request.method != "POST":
        return redirect("admin_TipoServicios")

    # Obtener la empresa activa
    empresa_activa = Empresa.objects.filter(activa=True).first()
    if not empresa_activa:
        messages.error(request, "No hay una empresa activa configurada.")
        return redirect("admin_TipoServicios")

    form = TipoServicioForm(request.POST, empresa=empresa_activa)
    next_url = request.POST.get("next") or reverse("admin_TipoServicios")

    if form.is_valid():
        tipo_servicio = form.save(commit=False)
        tipo_servicio.empresa = empresa_activa  # Asignar empresa activa
        tipo_servicio.save()
        messages.success(request, "Tipo de servicio creado correctamente.")
        return redirect(next_url)

    # Si hubo errores, guarda mensajes y regresa
    for field, errs in form.errors.items():
        for e in errs:
            messages.error(request, f"{field}: {e}")
    return redirect(next_url)

@login_required
def editar_tipo_servicio(request, pk):
    tipo = get_object_or_404(TipoServicio, pk=pk)
    if request.method == "POST":
        form = TipoServicioForm(request.POST, instance=tipo, empresa=tipo.empresa)
        if form.is_valid():
            form.save()
            messages.success(request, "Tipo de servicio actualizado.")
            return redirect("admin_TipoServicios")
    else:
        form = TipoServicioForm(instance=tipo, empresa=tipo.empresa)

    return render(request, "editar_tipo_servicio.html", {"form": form, "tipo": tipo})

@login_required
def eliminar_tipo_servicio(request, pk):
    tipo = get_object_or_404(TipoServicio, pk=pk)
    if request.method == "POST":
        tipo.delete()
        messages.success(request, "Tipo de servicio eliminado.")
        return redirect("admin_TipoServicios")
    # Confirmación simple (puedes usar modal también)
    return render(request, "confirmar_eliminar_tipo.html", {"tipo": tipo})


# ==================== GESTIÓN DE PEDIDOS ====================

@login_required
def admin_pedidos(request):
    """Lista de todos los pedidos"""
    empresa = Empresa.objects.filter(activa=True).first()
    
    # Obtener pedidos de la empresa activa
    pedidos = Pedido.objects.filter(empresa=empresa).select_related('usuario').prefetch_related('items').order_by('-fecha_pedido')
    
    # Filtro por estado
    estado = request.GET.get('estado')
    if estado:
        pedidos = pedidos.filter(estado=estado)
    
    # Búsqueda
    q = request.GET.get('q', '').strip()
    if q:
        pedidos = pedidos.filter(
            Q(numero_pedido__icontains=q) | 
            Q(nombre_cliente__icontains=q) | 
            Q(email_cliente__icontains=q) | 
            Q(telefono_cliente__icontains=q)
        )
    
    # Paginación
    paginator = Paginator(pedidos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total': pedidos.count(),
        'pendientes': pedidos.filter(estado='pendiente').count(),
        'confirmados': pedidos.filter(estado='confirmado').count(),
        'en_proceso': pedidos.filter(estado='en_proceso').count(),
        'entregados': pedidos.filter(estado='entregado').count(),
        'cancelados': pedidos.filter(estado='cancelado').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'query_actual': q,
        'estado_actual': estado,
        'estados': Pedido.ESTADO_CHOICES,
        'stats': stats,
    }
    return render(request, 'admin_pedidos.html', context)


@login_required
def admin_pedido_detalle(request, pedido_id):
    """Detalle de un pedido específico"""
    empresa = Empresa.objects.filter(activa=True).first()
    pedido = get_object_or_404(Pedido, id=pedido_id, empresa=empresa)
    
    context = {
        'pedido': pedido,
        'estados': Pedido.ESTADO_CHOICES,
    }
    return render(request, 'admin_pedido_detalle.html', context)


@login_required
def admin_cambiar_estado_pedido(request, pedido_id):
    """Cambiar el estado de un pedido"""
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')
    
    empresa = Empresa.objects.filter(activa=True).first()
    pedido = get_object_or_404(Pedido, id=pedido_id, empresa=empresa)
    
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(Pedido.ESTADO_CHOICES):
        pedido.estado = nuevo_estado
        pedido.save()
        
        # Registrar novedad
        registrar_novedad(
            request.user,
            f"Cambió el estado del pedido #{pedido.numero_pedido} a {pedido.get_estado_display()}"
        )
        
        messages.success(request, f'Estado del pedido actualizado a {pedido.get_estado_display()}')
    else:
        messages.error(request, 'Estado inválido')
    
    return redirect('admin_pedido_detalle', pedido_id=pedido.id)


@login_required
def admin_eliminar_pedido(request, pedido_id):
    """Eliminar un pedido (cancelar)"""
    if request.method == 'POST':
        empresa = Empresa.objects.filter(activa=True).first()
        pedido = get_object_or_404(Pedido, id=pedido_id, empresa=empresa)
        
        numero_pedido = pedido.numero_pedido
        pedido.delete()
        
        # Registrar novedad
        registrar_novedad(
            request.user,
            f"Eliminó el pedido #{numero_pedido}"
        )
        
        messages.success(request, f'Pedido #{numero_pedido} eliminado exitosamente')
        return redirect('admin_pedidos')
    
    return HttpResponseBadRequest('Método no permitido')