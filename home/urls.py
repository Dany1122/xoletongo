from django.urls import path
from .views import HomeView
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='home'),  # Usando la función index con secciones dinámicas
   # Acerca de Nosotros
    path('nosotros/', views.nosotros, name='nosotros'),

    # Servicios
    path('servicios/avistamiento/', views.avistamiento, name='avistamiento'),
    path('servicios/agroturismo/', views.agroturismo, name='agroturismo'),
    path('servicios/destilamiento/', views.destilamiento, name='destilamiento'),
    path('servicios/gastroturismo/', views.gastroturismo, name='gastroturismo'),
    path('servicios/talleres/', views.talleres, name='talleres'),
    path('servicios/senderismo/', views.senderismo, name='senderismo'),
    path('servicios/regenerativo/', views.regenerativo, name='regenerativo'),

    # Reservaciones
    path('reservaciones/hospedaje/', views.hospedaje, name='reservacion_hospedaje'),
    path('reservaciones/experiencia/', views.experiencia, name='experiencia'),

    # Temporada de luciérnagas
    path('reservaciones/luciernagas/hospedaje/', views.luciernagas_hospedaje, name='luciernagas_hospedaje'),
    path('reservaciones/luciernagas/transporte/', views.luciernagas_transporte, name='luciernagas_transporte'),
    path('reservaciones/luciernagas/comida/', views.luciernagas_comida, name='luciernagas_comida'),
    path('reservaciones/luciernagas/cena/', views.luciernagas_cena, name='luciernagas_cena'),
    path('reservaciones/luciernagas/visita/', views.luciernagas_visita, name='luciernagas_visita'),

    # Galería
    path('galeria/', views.galeria, name='galeria'), 

    # Contacto
    path('contacto/', views.contacto, name='contacto'),
    path('contacto/procesar/', views.procesar_contacto, name='procesar_contacto'),

    # E-commerce / Tienda
    path('productos/', views.productos, name='productos'),
    path('producto/<int:producto_id>/', views.producto_detalle, name='producto_detalle'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('procesar-pedido/', views.procesar_pedido, name='procesar_pedido'),
    path('confirmacion/<int:pedido_id>/', views.confirmacion_pedido, name='confirmacion_pedido'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)