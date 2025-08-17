from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    
    path('usuarios/', views.lista_usuarios, name='admin_usuarios'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='admin_editar_usuario'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='admin_eliminar_usuario'),
    path('usuarios/agregar/', views.agregar_usuario, name='admin_agregar_usuario'),
    path('ventas/', views.kanban_ventas, name='admin_ventas'),
    path("usuarios/exportar/pdf/", views.exportar_usuarios_pdf, name="admin_exportar_usuarios_pdf"),
    
    path('servicios/', views.lista_servicios, name='admin_servicios'),
    path('servicios/agregar', views.agregar_servicio, name='admin_agregar_servicio'),
    path('servicios/editar/<int:id>/', views.editar_servicio, name='admin_editar_servicio'),
    path('servicios/eliminar/<int:id>/', views.eliminar_servicio, name='admin_eliminar_servicio'),
    path("servicios/exportar/pdf/", views.exportar_servicios_pdf, name="admin_exportar_servicios_pdf"),

    path('productos/', views.admin_productos, name='admin_productos'),
    path('productos/agregar/', views.admin_agregar_producto, name='admin_agregar_producto'),
    path('categorias/crear/', views.crear_categoria_producto, name='crear_categoria_producto'),
    
    path('ventas/', views.kanban_ventas, name='admin_ventas'),
    path('ventas/exportar/pdf/', views.exportar_ventas_pdf, name='admin_exportar_pdf'),


    path('reservaciones/', views.lista_reservaciones, name='admin_reservaciones'),

    path('configuracion/', views.configuracion_empresa, name='configuracion_empresa'),
]