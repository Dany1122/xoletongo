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

    # Gestión de Roles
    path('roles/', views.gestion_roles, name='dev_gestion_roles'),
    path('roles/crear/', views.crear_rol, name='dev_crear_rol'),
    path('roles/editar/<int:pk>/', views.editar_rol, name='dev_editar_rol'),
    path('roles/eliminar/<int:pk>/', views.eliminar_rol, name='dev_eliminar_rol'),
    path('roles/toggle/<int:pk>/', views.toggle_rol_activo, name='dev_toggle_rol'),
    path('roles/<int:pk>/atributos/agregar/', views.agregar_atributo_rol, name='dev_agregar_atributo_rol'),
    path('roles/<int:pk>/atributos/eliminar/<str:atributo_nombre>/', views.eliminar_atributo_rol, name='dev_eliminar_atributo_rol'),
    
    # Ajustes Gráficos
    path('ajustes-graficos/', views.ajustes_graficos, name='dev_ajustes_graficos'),
    
    # Gestión de Staff
    path('staff/', views.gestion_staff, name='dev_gestion_staff'),
    path('staff/crear/', views.crear_staff, name='dev_crear_staff'),
    path('staff/editar/<int:pk>/', views.editar_staff, name='dev_editar_staff'),
    path('staff/eliminar/<int:pk>/', views.eliminar_staff, name='dev_eliminar_staff'),
    path('staff/toggle/<int:pk>/', views.toggle_staff_activo, name='dev_toggle_staff'),
    
    # Gestión de Módulos
    path('modulos/', views.gestion_modulos, name='dev_gestion_modulos'),
    path('modulos/productos/toggle/', views.toggle_modulo_productos, name='dev_toggle_productos'),
    path('modulos/resenas/toggle/', views.toggle_modulo_resenas, name='dev_toggle_resenas'),
]
