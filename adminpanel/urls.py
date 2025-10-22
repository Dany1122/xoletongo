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
    path('productos/editar/<int:pk>/', views.editar_producto, name='admin_editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='admin_eliminar_producto'),
    path('productos/exportar/pdf/', views.exportar_productos_pdf, name='admin_exportar_productos_pdf'),

    path('categorias/', views.lista_categorias, name='admin_categorias'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='admin_editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='admin_eliminar_categoria'),
    path('categorias/crear/', views.crear_categoria_producto, name='crear_categoria_producto'),
    
    path('ventas/', views.kanban_ventas, name='admin_ventas'),
    path('ventas/exportar/pdf/', views.exportar_ventas_pdf, name='admin_exportar_pdf'),

    path("tipos/", views.admin_tipos_servicio, name="admin_TipoServicios"),
    path("tipos/crear/", views.crear_tipo_servicio, name="crear_tipo_servicio"),
    path("tipos/<int:pk>/editar/", views.editar_tipo_servicio, name="editar_tipo_servicio"),
    path("tipos/<int:pk>/eliminar/", views.eliminar_tipo_servicio, name="eliminar_tipo_servicio"),
    

    path('reservaciones/', views.lista_reservaciones, name='admin_reservaciones'),
    path("reservas/exportar/pdf/", views.exportar_reservas_pdf, name="admin_exportar_reservas_pdf"),
    path("admin/reservaciones/", views.admin_reservaciones, name="admin_reservaciones"),
    path("admin/reservaciones/actualizar-estado/", views.admin_actualizar_estado_reservacion, name="admin_actualizar_estado_reservacion"),
    path("admin/reservaciones/exportar-pdf/", views.admin_exportar_reservas_pdf, name="admin_exportar_reservas_pdf"),

    path('configuracion/', views.configuracion_empresa, name='configuracion_empresa'),

    # Pedidos
    path('pedidos/', views.admin_pedidos, name='admin_pedidos'),
    path('pedidos/<int:pedido_id>/', views.admin_pedido_detalle, name='admin_pedido_detalle'),
    path('pedidos/<int:pedido_id>/cambiar-estado/', views.admin_cambiar_estado_pedido, name='admin_cambiar_estado_pedido'),
    path('pedidos/<int:pedido_id>/eliminar/', views.admin_eliminar_pedido, name='admin_eliminar_pedido'),
    
]