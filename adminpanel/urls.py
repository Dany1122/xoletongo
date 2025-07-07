from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('usuarios/', views.lista_usuarios, name='admin_usuarios'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='admin_editar_usuario'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='admin_eliminar_usuario'),
    path('usuarios/agregar/', views.agregar_usuario, name='admin_agregar_usuario'),
    path("usuarios/exportar/pdf/", views.exportar_usuarios_pdf,
         name="admin_exportar_usuarios_pdf"),
    path('ventas/', views.kanban_ventas, name='admin_ventas'),
]