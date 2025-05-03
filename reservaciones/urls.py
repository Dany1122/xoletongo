from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('reservar/<int:servicio_id>/', views.crear_reservacion, name='crear_reservacion'),
    path('reservaciones/procesar-pago/', views.procesar_pago, name='procesar_pago'),
    path('reservacion-exitosa/', views.reservacion_exitosa, name='reservacion_exitosa'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)