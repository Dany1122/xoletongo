from .forms import ReservacionAnonimaForm, ReservacionAutenticadaForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime
from django.conf import settings
from .models import Reservacion, Reservacion_servicio
from servicios.models import Servicio
from decimal import Decimal
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponseRedirect
import paypalrestsdk
from django.core.mail import send_mail
import os
from django.core.files.storage import FileSystemStorage
from empresas.models import Empresa
import mimetypes

# Create your views here.

def crear_reservacion(request, servicio_id):
    empresa = Empresa.objects.filter(activa=True).first()
    servicio = get_object_or_404(Servicio, id=servicio_id)

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReservacionAutenticadaForm(request.POST)
        else:
            form = ReservacionAnonimaForm(request.POST)

        if form.is_valid():
            reservacion = form.save(commit=False)
            if request.user.is_authenticated:
                reservacion.nombre_cliente = request.user.get_full_name() or request.user.username
                reservacion.email_cliente = request.user.email
            reservacion.pago_realizado = 'pago' in request.POST

        # Obtener y validar fechas y horas según tipo de servicio
        if servicio.servicio.tipo == 'porDia':
            try:
                fecha_inicio = datetime.strptime(request.POST['fecha_inicio'], "%Y-%m-%d").date()
                fecha_fin_str = request.POST.get('fecha_fin')
                if fecha_fin_str:
                    fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
                    if fecha_fin < fecha_inicio:
                        messages.error(request, "La fecha de fin no puede ser anterior a la fecha de inicio.")
                        return redirect(request.path)
                    noches = (fecha_fin - fecha_inicio).days or 1
                else:
                    fecha_fin = None
                    noches = 1
            except (KeyError, ValueError):
                messages.error(request, "Las fechas ingresadas no son válidas.")
                return redirect(request.path)
        else:
            fecha_inicio = datetime.strptime(request.POST['fecha_inicio'], "%Y-%m-%d").date()
            fecha_fin = None
            noches = 1

        # Obtener y validar hora de recepción
        hora_recepcion_str = request.POST.get('hora_recepcion')
        try:
            hora_recepcion = datetime.strptime(hora_recepcion_str, '%H:%M').time() if hora_recepcion_str else None
        except ValueError:
            messages.error(request, "La hora de recepción no es válida.")
            return redirect(request.path)

        numero_adultos = int(request.POST['adultos'])
        numero_ninos = int(request.POST['ninos'])
        numero_descuento = int(request.POST['descuento'])

        # Cálculo del total a pagar
        total = noches * (
            Decimal(servicio.costo_por_persona) * numero_adultos +
            Decimal(servicio.costo_niño) * numero_ninos +
            Decimal(servicio.costo_con_descuento) * numero_descuento
        )

        metodo_pago = request.POST.get('metodo_pago', '')
        quiere_pagar = request.POST.get('pago') == '1'

        if quiere_pagar:
            request.session['reservacion_datos'] = {
                'nombre_cliente': request.user.get_full_name() or request.user.username if request.user.is_authenticated else request.POST.get('nombre_cliente', ''),
                'email_cliente': request.user.email if request.user.is_authenticated else request.POST.get('email_cliente', ''),
                'fecha_inicio': fecha_inicio.strftime("%Y-%m-%d"),
                'fecha_fin': fecha_fin.strftime("%Y-%m-%d") if fecha_fin else '',
                'hora_recepcion': hora_recepcion.strftime('%H:%M') if hora_recepcion else '',
                'adultos': numero_adultos,
                'ninos': numero_ninos,
                'descuento': numero_descuento,
                'comentario': request.POST.get('comentario', ''),
                'servicio_id': servicio.id,
                'total': str(total),
                'metodo_pago': metodo_pago
            }
            if metodo_pago == 'paypal':
                return redirect('procesar_pago')
            elif metodo_pago == 'transferencia':
                return redirect('pago_transferencia')
            else:
                messages.error(request, "Método de pago no válido.")
                return redirect(request.path)
        else:
            reservacion = Reservacion.objects.create(
                empresa=empresa,
                nombre_cliente=request.user.get_full_name() or request.user.username if request.user.is_authenticated else request.POST.get('nombre_cliente', ''),
                email_cliente=request.user.email if request.user.is_authenticated else request.POST.get('email_cliente', ''),
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                hora_recepcion=hora_recepcion,
                numero_adultos=numero_adultos,
                numero_ninos=numero_ninos,
                numero_descuento=numero_descuento,
                comentario=request.POST.get('comentario', ''),
                pago_realizado=False,
                total_pagado=total
            )

            Reservacion_servicio.objects.create(
                id_reservacion=reservacion,
                servicio=servicio
            )

            if 'pago' in request.POST:
                request.session['reservacion_datos'] = {
                    'id': reservacion.id
                }
                return redirect('procesar_pago')
            else:
                enviar_correo_confirmacion(reservacion, servicio)
                return redirect('reservacion_exitosa')

    else:
        form = ReservacionAutenticadaForm() if request.user.is_authenticated else ReservacionAnonimaForm()

    return render(request, 'reservacion.html', {
        'form': form,
        'servicio': servicio,
        'tipo_servicio': servicio.servicio.tipo,
    })



paypalrestsdk.configure({
    'mode': settings.PAYPAL_MODE,  # 'sandbox' o 'live'
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_SECRET
})

def procesar_pago(request):
    datos = request.session.get('reservacion_datos')
    if not datos:
        return redirect('home')

    servicio = get_object_or_404(Servicio, id=datos['servicio_id'])

    if servicio.servicio.tipo == 'porDia':
        fecha_inicio = datetime.strptime(datos['fecha_inicio'], "%Y-%m-%d").date()
        fecha_fin = datos['fecha_fin']
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            noches = (fecha_fin - fecha_inicio).days or 1
        else:
            noches = 1
    else:
        fecha_inicio =  datetime.strptime(datos['fecha_inicio'], "%Y-%m-%d").date()
        fecha_fin = None
        noches = 1

    total = noches * (
        Decimal(servicio.costo_por_persona) * int(datos['adultos']) +
        Decimal(servicio.costo_niño) * int(datos['ninos']) +
        Decimal(servicio.costo_con_descuento) * int(datos['descuento'])
    )

    payment = paypalrestsdk.Payment({
        'intent': 'sale',
        'payer': {
            'payment_method': 'paypal'
        },
        'redirect_urls': {
            'return_url': request.build_absolute_uri('/pago-exitoso/'),
            'cancel_url': request.build_absolute_uri('/pago-cancelado/')
        },
        'transactions': [{
            'amount': {
                'total': str(total),
                'currency': 'MXN'
            },
            'description': f"Reservación para {servicio.titulo}"
        }]
    })

    if payment.create():
        approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
        return redirect(approval_url)
    else:
        return JsonResponse({'error': 'Error al crear el pago'}, status=400)

def reservacion_exitosa(request):
    return render(request, 'reservacion_exitosa.html')

@csrf_exempt
def pago_exitoso(request):
    datos = request.session.get('reservacion_datos')
    if not datos:
        return redirect('home')
    
    empresa = Empresa.objects.filter(activa=True).first()
    servicio = get_object_or_404(Servicio, id=datos['servicio_id'])

    if servicio.servicio.tipo == 'porDia':
        fecha_inicio = datetime.strptime(datos['fecha_inicio'], "%Y-%m-%d").date()
        fecha_fin = datos['fecha_fin']
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            noches = (fecha_fin - fecha_inicio).days or 1
        else:
            fecha_fin = None
            noches = 1
    else:
        fecha_inicio = datetime.strptime(datos['fecha_inicio'], "%Y-%m-%d").date()
        fecha_fin = None
        noches = 1

    hora_recepcion = datos.get('hora_recepcion')
    hora_recepcion = datetime.strptime(hora_recepcion, '%H:%M').time() if hora_recepcion else None

    total = noches * (
        Decimal(servicio.costo_por_persona) * int(datos['adultos']) +
        Decimal(servicio.costo_niño) * int(datos['ninos']) +
        Decimal(servicio.costo_con_descuento) * int(datos['descuento'])
    )

    reservacion = Reservacion.objects.create(
        empresa=empresa,
        nombre_cliente=datos['nombre_cliente'],
        email_cliente=datos['email_cliente'],
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        hora_recepcion=hora_recepcion,
        numero_adultos=datos['adultos'],
        numero_ninos=datos['ninos'],
        numero_descuento=datos['descuento'],
        comentario=datos.get('comentario', ''),
        pago_realizado=True,
        total_pagado=total
    )

    Reservacion_servicio.objects.create(
        id_reservacion=reservacion,
        servicio=servicio
    )

    enviar_correo_confirmacion(reservacion, servicio)
    del request.session['reservacion_datos']
    return redirect('reservacion_exitosa')

@csrf_exempt
def pago_cancelado(request):
    datos = request.session.get('reservacion_datos')
    if not datos:
        return redirect('home')
    empresa = Empresa.objects.filter(activa=True).first()
    servicio = get_object_or_404(Servicio, id=datos['servicio_id'])

    if servicio.servicio.tipo == 'porDia':
        fecha_inicio = datetime.strptime(datos['fecha_inicio'], "%Y-%m-%d").date()
        fecha_fin = datos['fecha_fin']
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            noches = (fecha_fin - fecha_inicio).days or 1
        else:
            fecha_fin = None
            noches = 1
    else:
        fecha_inicio = datetime.strptime(datos['fecha_inicio'], "%Y-%m-%d").date()
        fecha_fin = None
        noches = 1

    hora_recepcion = datos.get('hora_recepcion')
    hora_recepcion = datetime.strptime(hora_recepcion, '%H:%M').time() if hora_recepcion else None

    total = noches * (
        Decimal(servicio.costo_por_persona) * int(datos['adultos']) +
        Decimal(servicio.costo_niño) * int(datos['ninos']) +
        Decimal(servicio.costo_con_descuento) * int(datos['descuento'])
    )

    reservacion = Reservacion.objects.create(
        empresa=empresa,
        nombre_cliente=datos['nombre_cliente'],
        email_cliente=datos['email_cliente'],
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        hora_recepcion=hora_recepcion,
        numero_adultos=datos['adultos'],
        numero_ninos=datos['ninos'],
        numero_descuento=datos['descuento'],
        comentario=datos.get('comentario', ''),
        pago_realizado=False,
        total_pagado=total
    )

    Reservacion_servicio.objects.create(
        id_reservacion=reservacion,
        servicio=servicio
    )

    enviar_correo_confirmacion(reservacion, servicio)
    del request.session['reservacion_datos']
    messages.warning(request, "La reservación fue registrada, pero el pago no se completó.")
    return redirect('reservacion_exitosa')


def enviar_correo_confirmacion(reservacion, servicio):
    """
    Envía correo de confirmación de reservación.
    Si falla (por ejemplo, sin servidor SMTP en desarrollo), lo registra pero no interrumpe el flujo.
    """
    asunto = 'Confirmación de reservación'

    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2E86C1;">¡Gracias por tu reservación, {reservacion.nombre_cliente}!</h2>
            <p>Tu reservación para el servicio <strong>{servicio.titulo}</strong> ha sido registrada con éxito.</p>

            <h3>Detalles de la reservación:</h3>
            <ul>
                <li><strong>Fecha de inicio:</strong> {reservacion.fecha_inicio}</li>
                <li><strong>Fecha de fin:</strong> {reservacion.fecha_fin or 'N/A'}</li>
                <li><strong>Hora de recepción:</strong> {reservacion.hora_recepcion.strftime('%H:%M') if reservacion.hora_recepcion else 'N/A'}</li>
                <li><strong>Adultos:</strong> {reservacion.numero_adultos}</li>
                <li><strong>Niños:</strong> {reservacion.numero_ninos}</li>
                <li><strong>Personas con descuento:</strong> {reservacion.numero_descuento}</li>
                <li><strong>Total {'pagado' if reservacion.pago_realizado else 'a pagar'}:</strong> ${reservacion.total_pagado} MXN</li>
            </ul>

            <p>Si tienes alguna duda o deseas más información, puedes responder a este correo.</p>
            <p style="color: #888;">Este mensaje ha sido enviado automáticamente por el sistema de reservaciones.</p>
        </body>
    </html>
    """

    try:
        send_mail(
            subject=asunto,
            message='',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@xoletongo.com'),
            recipient_list=[reservacion.email_cliente],
            fail_silently=False,
            html_message=mensaje_html
        )
        print(f"✅ Correo de confirmación enviado a: {reservacion.email_cliente}")
    except Exception as e:
        # En desarrollo, si no hay servidor SMTP configurado, solo imprime el error
        print(f"⚠️ No se pudo enviar el correo de confirmación: {e}")
        print(f"📧 Destinatario: {reservacion.email_cliente}")
        print(f"📝 Asunto: {asunto}")
        if settings.DEBUG:
            print("💡 En desarrollo: configura un servidor SMTP o usa EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'")


@csrf_exempt
def pago_transferencia(request):
    datos = request.session.get('reservacion_datos')
    if not datos:
        return redirect('home')

    servicio = get_object_or_404(Servicio, id=datos['servicio_id'])
    empresa = Empresa.objects.filter(activa=True).first()

    if servicio.servicio.tipo == 'porDia':
        fecha_inicio = datetime.strptime(datos['fecha_inicio'], "%Y-%m-%d").date()
        fecha_fin = datos['fecha_fin']
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            noches = (fecha_fin - fecha_inicio).days or 1
        else:
            fecha_fin = None
            noches = 1
    else:
        fecha_inicio = datetime.strptime(datos['fecha_inicio'], "%Y-%m-%d").date()
        fecha_fin = None
        noches = 1

    hora_recepcion = datos.get('hora_recepcion')
    hora_recepcion = datetime.strptime(hora_recepcion, '%H:%M').time() if hora_recepcion else None

    total = noches * (
        Decimal(servicio.costo_por_persona) * int(datos['adultos']) +
        Decimal(servicio.costo_niño) * int(datos['ninos']) +
        Decimal(servicio.costo_con_descuento) * int(datos['descuento'])
    )

    if request.method == 'POST':
        archivo = request.FILES.get('comprobante')
        if archivo:
            tipo, _ = mimetypes.guess_type(archivo.name)
            if tipo in ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']:
                reservacion = Reservacion.objects.create(
                    empresa=empresa,
                    nombre_cliente=datos['nombre_cliente'],
                    email_cliente=datos['email_cliente'],
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    hora_recepcion=hora_recepcion,
                    numero_adultos=datos['adultos'],
                    numero_ninos=datos['ninos'],
                    numero_descuento=datos['descuento'],
                    comentario=datos.get('comentario', ''),
                    pago_realizado=False,
                    total_pagado=total,
                    comprobante_pago=archivo
                )

                Reservacion_servicio.objects.create(
                    id_reservacion=reservacion,
                    servicio=servicio
                )

                enviar_correo_confirmacion(reservacion, servicio)
                del request.session['reservacion_datos']
                messages.success(request, "Reservación registrada. Comprobante enviado.")
                return redirect('reservacion_exitosa')

    return render(request, 'pago_transferencia.html', {
        'empresa': empresa,
        'total': total
    })
