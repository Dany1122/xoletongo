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

# Create your views here.
def crear_reservacion(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)

    if request.method == 'POST':
        fecha_inicio = datetime.strptime(request.POST['fecha_inicio'], "%Y-%m-%d").date()
        fecha_fin = request.POST.get('fecha_fin')
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            if fecha_fin < fecha_inicio:
                messages.error(request, "La fecha de fin no puede ser anterior a la fecha de inicio.")
                return redirect(request.path)

        numero_adultos = int(request.POST['adultos'])
        numero_ninos = int(request.POST['ninos'])
        numero_descuento = int(request.POST['descuento'])

        # Cálculo del total a pagar
        total = (
            Decimal(servicio.costo_por_persona) * numero_adultos +
            Decimal(servicio.costo_niño) * numero_ninos +
            Decimal(servicio.costo_con_descuento) * numero_descuento
        )

        if 'pago' in request.POST:
            # Guardar datos en sesión para redirigir al pago
            request.session['reservacion_datos'] = {
                'nombre_cliente': request.POST['nombre_cliente'],
                'email_cliente': request.POST['email_cliente'],
                'fecha_inicio': request.POST['fecha_inicio'],
                'fecha_fin': request.POST.get('fecha_fin', ''),
                'adultos': numero_adultos,
                'ninos': numero_ninos,
                'descuento': numero_descuento,
                'comentario': request.POST.get('comentario', ''),
                'servicio_id': servicio.id,
                'total': str(total)  # opcional: guarda el total para mostrar en procesar_pago
            }
            return redirect('procesar_pago')
        else:
            # Crear reserva sin pago inmediato
            reservacion = Reservacion.objects.create(
                nombre_cliente=request.POST['nombre_cliente'],
                email_cliente=request.POST['email_cliente'],
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin if fecha_fin else None,
                numero_adultos=numero_adultos,
                numero_ninos=numero_ninos,
                numero_descuento=numero_descuento,
                comentario=request.POST.get('comentario', ''),
                pago_realizado=False,
                total_pagado=total  # Aquí se almacena el total
            )

            Reservacion_servicio.objects.create(
                id_reservacion=reservacion,
                servicio=servicio
            )
            enviar_correo_confirmacion(reservacion, servicio)
            return redirect('reservacion_exitosa')

    return render(request, 'reservacion.html', {'servicio': servicio})

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

    # Calcular el total
    total = (
        Decimal(servicio.costo_por_persona) * int(datos['adultos']) +
        Decimal(servicio.costo_niño) * int(datos['ninos']) +
        Decimal(servicio.costo_con_descuento) * int(datos['descuento'])
    )

    # Crear un pago en PayPal
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
        # Encuentra el link de aprobación y redirige a PayPal para que el usuario apruebe el pago
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

    servicio = get_object_or_404(Servicio, id=datos['servicio_id'])

    # Calcular total
    total = (
        Decimal(servicio.costo_por_persona) * int(datos['adultos']) +
        Decimal(servicio.costo_niño) * int(datos['ninos']) +
        Decimal(servicio.costo_con_descuento) * int(datos['descuento'])
    )

    # Crear la reservación con pago confirmado
    reservacion = Reservacion.objects.create(
        nombre_cliente=datos['nombre_cliente'],
        email_cliente=datos['email_cliente'],
        fecha_inicio=datos['fecha_inicio'],
        fecha_fin=datos['fecha_fin'] if datos['fecha_fin'] else None,
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

    # Enviar correo con HTML
    enviar_correo_confirmacion(reservacion, servicio)

    # Limpia la sesión
    del request.session['reservacion_datos']

    return redirect('reservacion_exitosa')

@csrf_exempt
def pago_cancelado(request):
    datos = request.session.get('reservacion_datos')
    if not datos:
        return redirect('home')

    servicio = get_object_or_404(Servicio, id=datos['servicio_id'])

    # Calcular total
    total = (
        Decimal(servicio.costo_por_persona) * int(datos['adultos']) +
        Decimal(servicio.costo_niño) * int(datos['ninos']) +
        Decimal(servicio.costo_con_descuento) * int(datos['descuento'])
    )

    # Guardar reservación sin pago
    reservacion = Reservacion.objects.create(
        nombre_cliente=datos['nombre_cliente'],
        email_cliente=datos['email_cliente'],
        fecha_inicio=datos['fecha_inicio'],
        fecha_fin=datos['fecha_fin'] if datos['fecha_fin'] else None,
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

    # Enviar correo de confirmación indicando que el pago no se completó
    enviar_correo_confirmacion(reservacion, servicio)

    # Limpiar sesión
    del request.session['reservacion_datos']

    messages.warning(request, "La reservación fue registrada, pero el pago no se completó.")
    return redirect('reservacion_exitosa')


def enviar_correo_confirmacion(reservacion, servicio):
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

    send_mail(
        subject=asunto,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reservacion.email_cliente],
        fail_silently=False,
        html_message=mensaje_html
    )