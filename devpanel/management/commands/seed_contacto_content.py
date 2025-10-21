from django.core.management.base import BaseCommand
from empresas.models import Empresa
from devpanel.models import Pagina, Seccion


class Command(BaseCommand):
    help = 'Seeds content for Contacto page into Pagina and Seccion models.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏢 Migrando contenido de: Contacto (Xoletongo)'))

        try:
            xoletongo_empresa = Empresa.objects.get(nombre='Xoletongo')
        except Empresa.DoesNotExist:
            self.stderr.write(self.style.ERROR('❌ Empresa "Xoletongo" no encontrada. Asegúrate de que exista.'))
            return

        # --- Obtener o crear la página Contacto ---
        contacto_page, created = Pagina.objects.get_or_create(
            empresa=xoletongo_empresa,
            slug='contacto',
            defaults={'titulo': 'Contáctanos', 'activa': True}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'📄 Creando página: {contacto_page.get_slug_display()}...'))
        else:
            self.stdout.write(self.style.SUCCESS(f'📄 Actualizando página: {contacto_page.get_slug_display()}...'))

        # --- Eliminar secciones existentes para evitar duplicados ---
        Seccion.objects.filter(pagina=contacto_page).delete()

        # --- Secciones de la página Contacto ---
        secciones_data = [
            # 1. Hero/Breadcrumb
            {
                'tipo': 'hero',
                'titulo': 'Hero Contacto',
                'orden': 1,
                'configuracion': {
                    'titulo': 'Contactanos',
                    'bg_class': 'breadcam_bg_2'
                }
            },
            # 2. Mapa de Google
            {
                'tipo': 'mapa',
                'titulo': 'Ubicación',
                'orden': 2,
                'configuracion': {
                    'iframe_src': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d7523.381819402622!2d-98.55339850642092!3d19.4688888!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x85d1d147b7c8f5f9%3A0x8bdf72377f84c714!2sxoletongo%20centro%20de%20avistamiento!5e0!3m2!1ses-419!2smx!4v1744957182871!5m2!1ses-419!2smx',
                    'width': '600',
                    'height': '450'
                }
            },
            # 3. Formulario de contacto + Info
            {
                'tipo': 'contacto_form',
                'titulo': 'Formulario de Contacto',
                'orden': 3,
                'configuracion': {
                    'titulo': 'Contactanos',
                    'action': 'contact_process.php',
                    'info_contacto': [
                        {
                            'icono': 'ti-home',
                            'titulo': 'Tlaxcala, San Felipe Hidalgo',
                            'subtitulo': 'Santa Cruz Moxolahua km 15, 90288'
                        },
                        {
                            'icono': 'ti-tablet',
                            'titulo': '748 106 5103',
                            'subtitulo': 'Todos los dias 10am a 11pm'
                        },
                        {
                            'icono': 'ti-email',
                            'titulo': 'xoletongo.santuario@gmail.com',
                            'subtitulo': ''
                        }
                    ]
                }
            }
        ]

        for data in secciones_data:
            Seccion.objects.create(pagina=contacto_page, **data)
            self.stdout.write(self.style.SUCCESS(f'  ✓ {data["tipo"].capitalize()} "{data["titulo"]}" creado'))

        self.stdout.write(self.style.SUCCESS('\n✅ ¡Migración de Contacto completada exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'   Total de secciones creadas: {Seccion.objects.filter(pagina=contacto_page).count()}'))

