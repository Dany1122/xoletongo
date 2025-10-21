from django.core.management.base import BaseCommand
from empresas.models import Empresa
from devpanel.models import Pagina, Seccion


class Command(BaseCommand):
    help = 'Seeds content for Servicios page into Pagina and Seccion models.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏢 Migrando contenido de: Servicios (Xoletongo)'))

        try:
            xoletongo_empresa = Empresa.objects.get(nombre='Xoletongo')
        except Empresa.DoesNotExist:
            self.stderr.write(self.style.ERROR('❌ Empresa "Xoletongo" no encontrada. Asegúrate de que exista.'))
            return

        # --- Obtener o crear la página Servicios ---
        servicios_page, created = Pagina.objects.get_or_create(
            empresa=xoletongo_empresa,
            slug='servicios',
            defaults={'titulo': 'Nuestros Servicios', 'activa': True}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'📄 Creando página: {servicios_page.get_slug_display()}...'))
        else:
            self.stdout.write(self.style.SUCCESS(f'📄 Actualizando página: {servicios_page.get_slug_display()}...'))

        # --- Eliminar secciones existentes para evitar duplicados ---
        Seccion.objects.filter(pagina=servicios_page).delete()

        # --- Secciones de la página Servicios ---
        secciones_data = [
            # 1. Hero/Breadcrumb (MODIFICABLE)
            {
                'tipo': 'hero',
                'titulo': 'Hero Servicios',
                'orden': 1,
                'configuracion': {
                    'titulo': 'Nuestros Servicios',
                    'bg_class': 'breadcam_bg_2'
                }
            },
            # 2. Tarjetas de Servicios (OBLIGATORIO - lee desde BD)
            {
                'tipo': 'servicios_accordion',
                'titulo': 'Listado de Servicios',
                'orden': 2,
                'configuracion': {
                    'titulo': '',  # Opcional: título adicional antes del accordion
                    'subtitulo': '',  # Opcional: subtítulo descriptivo
                    'descripcion': 'Esta sección muestra todos los servicios organizados por tipo. Los servicios se cargan automáticamente desde la base de datos.'
                }
            }
        ]

        for data in secciones_data:
            Seccion.objects.create(pagina=servicios_page, **data)
            self.stdout.write(self.style.SUCCESS(f'  ✓ {data["tipo"].capitalize()} "{data["titulo"]}" creado'))

        self.stdout.write(self.style.SUCCESS('\n✅ ¡Migración de Servicios completada exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'   Total de secciones creadas: {Seccion.objects.filter(pagina=servicios_page).count()}'))
        self.stdout.write(self.style.WARNING('\n⚠️  NOTA IMPORTANTE:'))
        self.stdout.write(self.style.WARNING('   La sección "Tarjetas de Servicios" es OBLIGATORIA y no debe eliminarse.'))
        self.stdout.write(self.style.WARNING('   Es la que muestra los servicios y permite hacer reservaciones.'))
        self.stdout.write(self.style.SUCCESS('\n💡 Puedes agregar más secciones (texto, features, CTA, etc.) desde el DevPanel.'))

