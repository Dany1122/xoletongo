from django.core.management.base import BaseCommand
from devpanel.models import Seccion

class Command(BaseCommand):
    help = 'Actualiza los colores del botón de contacto'

    def handle(self, *args, **options):
        # Buscar la sección de contacto
        seccion = Seccion.objects.filter(tipo='contacto_form').first()

        if seccion:
            self.stdout.write(f'✓ Sección encontrada: {seccion.titulo}')
            
            # Actualizar colores
            # Verde Bosque con texto blanco para estado normal
            seccion.configuracion['boton_bg_color'] = '#2d6a4f'
            seccion.configuracion['boton_text_color'] = '#ffffff'
            
            # Verde Menta brillante para hover
            seccion.configuracion['boton_hover_color'] = '#40c057'
            
            seccion.save()
            
            self.stdout.write(self.style.SUCCESS('\n✓ Colores actualizados exitosamente:'))
            self.stdout.write(f'  - Color de fondo: {seccion.configuracion.get("boton_bg_color", "No definido")}')
            self.stdout.write(f'  - Color de texto: {seccion.configuracion.get("boton_text_color", "No definido")}')
            self.stdout.write(self.style.SUCCESS(f'  - Color hover: {seccion.configuracion["boton_hover_color"]} (verde)'))
        else:
            self.stdout.write(self.style.ERROR('No se encontró la sección de contacto'))

