from django.core.management.base import BaseCommand
from empresas.models import Empresa
from devpanel.models import Pagina, Seccion


class Command(BaseCommand):
    help = 'Seeds content for Galeria page into Pagina and Seccion models.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏢 Migrando contenido de: Galería (Xoletongo)'))

        try:
            xoletongo_empresa = Empresa.objects.get(nombre='Xoletongo')
        except Empresa.DoesNotExist:
            self.stderr.write(self.style.ERROR('❌ Empresa "Xoletongo" no encontrada. Asegúrate de que exista.'))
            return

        # --- Obtener o crear la página Galería ---
        galeria_page, created = Pagina.objects.get_or_create(
            empresa=xoletongo_empresa,
            slug='galeria',
            defaults={'titulo': 'Galería de Imágenes', 'activa': True}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'📄 Creando página: {galeria_page.get_slug_display()}...'))
        else:
            self.stdout.write(self.style.SUCCESS(f'📄 Actualizando página: {galeria_page.get_slug_display()}...'))

        # --- Eliminar secciones existentes para evitar duplicados ---
        Seccion.objects.filter(pagina=galeria_page).delete()

        # --- Secciones de la página Galería ---
        secciones_data = [
            # 1. Hero/Breadcrumb
            {
                'tipo': 'hero',
                'titulo': 'Hero Galería',
                'orden': 1,
                'configuracion': {
                    'titulo': 'Galería de Imágenes',
                    'bg_class': 'breadcam_bg_2'
                }
            },
            # 2. Galería dinámica (lee imágenes desde ImagenServicio)
            {
                'tipo': 'galeria',
                'titulo': 'Galería de Servicios',
                'orden': 2,
                'configuracion': {
                    'tipo': 'dinamica',  # Indica que lee desde BD
                    'descripcion': 'Imágenes de nuestros servicios y experiencias'
                }
            }
        ]

        for data in secciones_data:
            Seccion.objects.create(pagina=galeria_page, **data)
            self.stdout.write(self.style.SUCCESS(f'  ✓ {data["tipo"].capitalize()} "{data["titulo"]}" creado'))

        self.stdout.write(self.style.SUCCESS('\n✅ ¡Migración de Galería completada exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'   Total de secciones creadas: {Seccion.objects.filter(pagina=galeria_page).count()}'))

