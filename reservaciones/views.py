from django.shortcuts import render, get_object_or_404, redirect
from .models import Servicio, Reservacion, Reservacion_servicio
from .forms import ReservacionAnonimaForm, ReservacionAutenticadaForm
from django.contrib.auth.decorators import login_required


# Create your views here.
def crear_reservacion(request, servicio_id):
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
            reservacion.save()

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
                return redirect('reservacion_exitosa')

    else:
        form = ReservacionAutenticadaForm() if request.user.is_authenticated else ReservacionAnonimaForm()

    return render(request, 'reservacion.html', {'form': form, 'servicio': servicio})


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