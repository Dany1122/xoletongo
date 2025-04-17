from django.urls import path
from .views import HomeView
from . import views

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
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

    #Login
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),


]