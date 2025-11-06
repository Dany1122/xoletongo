from django.core.management.base import BaseCommand
from empresas.models import Empresa
from devpanel.models import Pagina, Seccion


class Command(BaseCommand):
    help = 'Seeds content for Nosotros page into Pagina and Seccion models.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏢 Migrando contenido de: Nosotros (Xoletongo)'))

        try:
            xoletongo_empresa = Empresa.objects.get(nombre='Xoletongo')
        except Empresa.DoesNotExist:
            self.stderr.write(self.style.ERROR('❌ Empresa "Xoletongo" no encontrada. Asegúrate de que exista.'))
            return

        # --- Obtener o crear la página Nosotros ---
        nosotros_page, created = Pagina.objects.get_or_create(
            empresa=xoletongo_empresa,
            slug='nosotros',
            defaults={'titulo': 'Sobre Nosotros', 'activa': True}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'📄 Creando página: {nosotros_page.get_slug_display()}...'))
        else:
            self.stdout.write(self.style.SUCCESS(f'📄 Actualizando página: {nosotros_page.get_slug_display()}...'))

        # --- Eliminar secciones existentes para evitar duplicados ---
        Seccion.objects.filter(pagina=nosotros_page).delete()

        # --- Secciones de la página Nosotros ---
        secciones_data = [
            # 1. Hero/Breadcrumb
            {
                'tipo': 'hero',
                'titulo': 'Hero Nosotros',
                'orden': 1,
                'configuracion': {
                    'titulo': 'Sobre nosotros',
                    'bg_class': 'breadcam_bg'
                }
            },
            # 2. Features Cards (Objetivo, Visión, Misión)
            {
                'tipo': 'features',
                'titulo': 'Objetivo, Visión y Misión',
                'orden': 2,
                'configuracion': {
                    'estilo': 'cards',  # Para usar features_cards.html
                    'items': [
                        {
                            'titulo': 'Objetivo',
                            'descripcion': 'Cuidar y mantener el medio ambiente del entorno natural de la flora y fauna en condiciones óptimas, para la conservación de nuestros bosques y aprovecharlos de manera no extractiva para el disfrute de quien guste de la naturaleza.'
                        },
                        {
                            'titulo': 'Visión',
                            'descripcion': 'Ofrecer experiencias vivas de calidad bajo normas sustentables, y que los visitantes se lleven un bonito recuerdo.'
                        },
                        {
                            'titulo': 'Misión',
                            'descripcion': 'Rescatar y conservar las tradiciones y costumbres de nuestros Pueblos, bajo una base de sustentabilidad amigable con el medio ambiente.'
                        }
                    ]
                }
            },
            # 3. Bloque de texto con imágenes (DESDE EL CORAZÓN)
            {
                'tipo': 'texto',
                'titulo': 'Desde el Corazón',
                'orden': 3,
                'configuracion': {
                    'layout': 'imagen_derecha',
                    'span_titulo': 'Xoletongo',
                    'titulo': 'DESDE EL CORAZÓN',
                    'parrafo': 'En el espolón de la sierra nevada del Ixtapopo, en el municipio de Nanacamilpa de Mariano Arista estado de Tlaxcala, en los bosques de coníferas en la comunidad de San Felipe Hidalgo encontrarás un lugar que te ofrece las mejores experiencias en Turismo de Naturaleza y Gastro Turismo, sobre todo en los meses de junio, julio y agosto; en donde la oscuridad en el bosque se llena de magia con miles de destellos bioluminiscentes que emiten las luciérnagas, en un ritual lleno de misticismo.',
                    'boton_texto': 'Learn More',
                    'boton_url': '#',
                    'imagen_1': 'img/about/about_1.png',
                    'imagen_2': 'img/about/about_2.png'
                }
            },
            # 4. Carousel simple de imágenes
            {
                'tipo': 'carousel',
                'titulo': 'Galería de Experiencias',
                'orden': 4,
                'configuracion': {
                    'estilo': 'simple',  # Para usar carousel_simple.html
                    'slides': [
                        {'bg_class': 'about_bg_1'},
                        {'bg_class': 'about_bg_1'},
                        {'bg_class': 'about_bg_1'},
                        {'bg_class': 'about_bg_1'}
                    ]
                }
            },
            # 5. CTA de WhatsApp
            {
                'tipo': 'cta',
                'titulo': 'Contacto WhatsApp',
                'orden': 5,
                'configuracion': {
                    'tipo': 'whatsapp',
                    'pregunta': '¿Tienes alguna pregunta? ¡Contáctanos!',
                    'numero_whatsapp': '+52 748 106 5103',
                    'url_whatsapp': 'https://wa.me/5211234567890'
                }
            },
            # 6. Instagram Feed
            {
                'tipo': 'instagram',
                'titulo': 'Síguenos en Instagram',
                'orden': 6,
                'configuracion': {
                    'imagenes': [
                        {'imagen': 'img/instragram/1.png', 'alt': 'Instagram 1', 'url': '#'},
                        {'imagen': 'img/instragram/2.png', 'alt': 'Instagram 2', 'url': '#'},
                        {'imagen': 'img/instragram/3.png', 'alt': 'Instagram 3', 'url': '#'},
                        {'imagen': 'img/instragram/4.png', 'alt': 'Instagram 4', 'url': '#'},
                        {'imagen': 'img/instragram/5.png', 'alt': 'Instagram 5', 'url': '#'}
                    ]
                }
            }
        ]

        for data in secciones_data:
            Seccion.objects.create(pagina=nosotros_page, **data)
            self.stdout.write(self.style.SUCCESS(f'  ✓ {data["tipo"].capitalize()} "{data["titulo"]}" creado'))

        self.stdout.write(self.style.SUCCESS('\n✅ ¡Migración de Nosotros completada exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'   Total de secciones creadas: {Seccion.objects.filter(pagina=nosotros_page).count()}'))

