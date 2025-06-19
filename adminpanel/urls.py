from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('usuarios/', views.lista_usuarios, name='admin_usuarios'),
    path('usuarios/editar/<int:id>/', views.editar_usuario, name='admin_editar_usuario'),
    path('usuarios/eliminar/<int:id>/', views.eliminar_usuario, name='admin_eliminar_usuario'),
]