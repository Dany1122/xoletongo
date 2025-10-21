# devpanel/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('empresas/', views.gestion_empresas, name='dev_gestion_empresas'),
    path('empresas/activar/<int:pk>/', views.activar_empresa_dev, name='dev_activar_empresa'),
    path('empresas/crear/', views.crear_empresa, name='dev_crear_empresa'),
    path('empresas/editar/<int:pk>/', views.editar_empresa, name='dev_editar_empresa'),

    path('modelos/', views.gestion_modelos, name='dev_gestion_modelos'),
    path('modelos/crear/', views.crear_atributo, name='dev_crear_atributo'),
    path('modelos/editar/<int:pk>/', views.editar_atributo, name='dev_editar_atributo'),
    path('modelos/eliminar/<int:pk>/', views.eliminar_atributo, name='dev_eliminar_atributo'),

    path('secciones/', views.gestion_secciones, name='dev_gestion_secciones'),
    path('secciones/<str:slug_pagina>/', views.gestion_secciones_pagina, name='dev_gestion_secciones_pagina'),
    path('secciones/<str:slug_pagina>/crear/', views.crear_seccion, name='dev_crear_seccion'),
    path('secciones/editar/<int:pk>/', views.editar_seccion, name='dev_editar_seccion'),
    path('secciones/eliminar/<int:pk>/', views.eliminar_seccion, name='dev_eliminar_seccion'),
    path('secciones/orden/<int:pk>/<str:direccion>/', views.cambiar_orden_seccion, name='dev_cambiar_orden_seccion'),
    path('secciones/toggle/<int:pk>/', views.toggle_seccion_activa, name='dev_toggle_seccion'),
]
