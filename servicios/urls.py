from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('servicios/<int:servicio_id>/', views.detalle_servicio, name='detalle_servicio'),
    path('servicios/', views.servicios_por_tipo, name='servicios_por_tipo'),
    
    # URLs para reseñas
    path('resena/crear/<int:content_type_id>/<int:object_id>/', views.crear_resena, name='crear_resena'),
    path('resena/editar/<int:resena_id>/', views.editar_resena, name='editar_resena'),
    path('resena/eliminar/<int:resena_id>/', views.eliminar_resena, name='eliminar_resena'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
