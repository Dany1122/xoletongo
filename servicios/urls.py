from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('servicios/<int:servicio_id>/', views.detalle_servicio, name='detalle_servicio'),
    path('servicios/', views.servicios_por_tipo, name='servicios_por_tipo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
