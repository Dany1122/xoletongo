from django.shortcuts import render, get_object_or_404, redirect
from .models import Servicio, Reservacion, Reservacion_servicio

# Create your views here.
def crear_reservacion(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)

    if request.method == 'POST':
        if 'pago' in request.POST:
            # Si quiere pagar, pasamos la info temporalmente
            request.session['reservacion_datos'] = {
                'nombre_cliente': request.POST['nombre_cliente'],
                'email_cliente': request.POST['email_cliente'],
                'fecha_inicio': request.POST['fecha_inicio'],
                'fecha_fin': request.POST.get('fecha_fin', ''),
                'numero_personas': request.POST['numero_personas'],
                'comentario': request.POST.get('comentario', ''),
                'servicio_id': servicio.id
            }
            return redirect('procesar_pago')  # Redirige a la vista de pago
        
        else:
            # Si NO quiere pagar, crea directamente la reservación
            reservacion = Reservacion.objects.create(
                nombre_cliente=request.POST['nombre_cliente'],
                email_cliente=request.POST['email_cliente'],
                fecha_inicio=request.POST['fecha_inicio'],
                fecha_fin=request.POST.get('fecha_fin', None),
                numero_personas=request.POST['numero_personas'],
                comentario=request.POST.get('comentario', ''),
                pago_realizado=False
            )

            Reservacion_servicio.objects.create(
                id_reservacion=reservacion,
                servicio=servicio
            )

            return redirect('reservacion_exitosa')

    return render(request, 'reservacion.html', {'servicio': servicio})

def procesar_pago(request):
    if request.method == 'POST':
        # Procesa el pago (ficticio)
        datos = request.session.get('reservacion_datos')
        if not datos:
            return redirect('home')  # Seguridad: si no hay datos, redirige

        servicio = get_object_or_404(Servicio, id=datos['servicio_id'])

        reservacion = Reservacion.objects.create(
            nombre_cliente=datos['nombre_cliente'],
            email_cliente=datos['email_cliente'],
            fecha_inicio=datos['fecha_inicio'],
            fecha_fin=datos['fecha_fin'] if datos['fecha_fin'] else None,
            numero_personas=datos['numero_personas'],
            comentario=datos['comentario'],
            pago_realizado=True  # Aquí se registra que pagó
        )

        Reservacion_servicio.objects.create(
            id_reservacion=reservacion,
            servicio=servicio
        )

        del request.session['reservacion_datos']  # Limpia los datos temporales

        return redirect('reservacion_exitosa')

    return render(request, 'procesar_pago.html')

def reservacion_exitosa(request):
    return render(request, 'reservacion_exitosa.html')