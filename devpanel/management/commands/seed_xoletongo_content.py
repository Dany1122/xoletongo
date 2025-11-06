from django.core.management.base import BaseCommand
from empresas.models import Empresa
from devpanel.models import Pagina, Seccion


class Command(BaseCommand):
    help = 'Migra el contenido actual de Xoletongo al nuevo sistema de secciones'

    def handle(self, *args, **kwargs):
        try:
            xoletongo = Empresa.objects.get(nombre='Xoletongo')
        except Empresa.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ No se encontró la empresa Xoletongo'))
            return

        self.stdout.write(self.style.SUCCESS(f'🏢 Migrando contenido de: {xoletongo.nombre}'))

        # Eliminar páginas existentes para evitar duplicados
        Pagina.objects.filter(empresa=xoletongo).delete()

        # ====== PÁGINA: HOME ======
        self.stdout.write('📄 Creando página: Home...')
        home = Pagina.objects.create(
            empresa=xoletongo,
            slug='home',
            titulo='Inicio',
            activa=True
        )

        # Sección 1: Carousel Hero
        Seccion.objects.create(
            pagina=home,
            tipo='carousel',
            titulo='Carousel Principal',
            orden=1,
            activa=True,
            configuracion={
                'slides': [
                    {
                        'titulo': '¡Tlaxcala brilla!',
                        'subtitulo': 'Santuario de las luciérnagas',
                        'imagen_css_class': 'slider_bg_1'
                    },
                    {
                        'titulo': 'Conexión con la Naturaleza',
                        'subtitulo': 'Un paseo nocturno dentro de los bosques de coníferas, donde las noches se vuelven mágicas.',
                        'imagen_css_class': 'slider_bg_2'
                    },
                    {
                        'titulo': 'Hospitalidad en la Sierra',
                        'subtitulo': 'Hospédate con nosotros y descubre un entorno único',
                        'imagen_css_class': 'slider_bg_3'
                    }
                ]
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✓ Carousel creado'))

        # Sección 2: About - Visita Xoletongo
        Seccion.objects.create(
            pagina=home,
            tipo='texto',
            titulo='Comienza la aventura',
            orden=2,
            activa=True,
            configuracion={
                'subtitulo': 'Comienza la aventura',
                'titulo': 'Visita Xoletongo',
                'contenido': 'Empresa familiar apasionada por la comida tradicional Tlaxcalteca, y comprometida con el rescate de las recetas de herencia e historia. Ofrecemos experiencias vivas, con base en las tradiciones y costumbres de nuestros Pueblos.',
                'boton_texto': 'Conoce más',
                'boton_url': '#',
                'imagen_1': 'img/about/about_1.png',
                'imagen_2': 'img/about/about_2.png',
                'layout': 'text-left-images-right'
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✓ About "Visita Xoletongo" creado'))

        # Sección 3: Servicios Disponibles
        Seccion.objects.create(
            pagina=home,
            tipo='features',
            titulo='Servicios Disponibles',
            orden=3,
            activa=True,
            configuracion={
                'subtitulo': '¿Qué ofrecemos?',
                'titulo': 'Servicios Disponibles',
                'items': [
                    {
                        'titulo': 'Gastroturismo',
                        'descripcion': 'Degustaciones de platillos tradicionales con ingredientes prehispánicos.',
                        'imagen': 'img/offers/gastroturismo.png',
                        'url': '{% url "gastroturismo" %}'
                    },
                    {
                        'titulo': 'Agroturismo',
                        'descripcion': 'Recolectamos productos del campo listos para cocinarse.',
                        'imagen': 'img/offers/agroturismo.png',
                        'url': '{% url "agroturismo" %}'
                    },
                    {
                        'titulo': 'Turismo Regenerativo',
                        'descripcion': 'Convivencia con las comunidades locales y su día a día.',
                        'imagen': 'img/offers/regenerativo.png',
                        'url': '{% url "regenerativo" %}'
                    },
                    {
                        'titulo': 'Destilado Artesanal',
                        'descripcion': 'Destilación artesanal de agave con sal de gusano Chinicuil.',
                        'imagen': 'img/offers/destilado.png',
                        'url': '{% url "destilamiento" %}'
                    },
                    {
                        'titulo': 'Senderismo',
                        'descripcion': 'Interpretación ambiental de flora y fauna local.',
                        'imagen': 'img/offers/senderismo.png',
                        'url': '{% url "senderismo" %}'
                    },
                    {
                        'titulo': 'Avistamiento de Luciérnagas',
                        'descripcion': 'Experiencia mágica en temporada de junio a agosto.',
                        'imagen': 'img/offers/luciernagas.png',
                        'url': '{% url "avistamiento" %}'
                    },
                    {
                        'titulo': 'Talleres',
                        'descripcion': 'Elaboración de pan de pulque y otros alimentos tradicionales.',
                        'imagen': 'img/offers/talleres.png',
                        'url': '{% url "talleres" %}'
                    }
                ]
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✓ Servicios Disponibles creado'))

        # Sección 4: Reconocimientos
        Seccion.objects.create(
            pagina=home,
            tipo='testimonios',
            titulo='Reconocimientos',
            orden=4,
            activa=True,
            configuracion={
                'subtitulo': 'Nos esmeramos para darte el mejor servicio',
                'titulo': 'RECONOCIMIENTOS',
                'items': [
                    {
                        'titulo': 'Ven a comer 2017',
                        'descripcion': 'Primer lugar como emprendedores e innovación del producto gastronómico otorgado por la Secretaría de Turismo Federal.',
                        'imagen': 'img/reconocimientos/comer.png'
                    },
                    {
                        'titulo': 'Embajador Gastronómico y Turístico',
                        'descripcion': 'Reconocimiento otorgado por la Secretaría de Turismo y Cultura del Estado de Tlaxcala.',
                        'imagen': 'img/reconocimientos/embajador.png'
                    },
                    {
                        'titulo': 'Guardiana de la Cocina Tradicional',
                        'descripcion': 'Reconocimiento a Norma Muñoz Brindis por la Secretaría de Cultura Federal.',
                        'imagen': 'img/reconocimientos/guardiana.png'
                    }
                ],
                'video': 'img/Xoletongo_vid.mp4'
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✓ Reconocimientos creado'))

        # Sección 5: Gastronomía Ancestral
        Seccion.objects.create(
            pagina=home,
            tipo='texto',
            titulo='Gastronomía Ancestral',
            orden=5,
            activa=True,
            configuracion={
                'subtitulo': 'Gastronomía Ancestral',
                'titulo': 'Sabores auténticos con historia y tradición',
                'contenido': 'En Xoletongo celebramos la cocina tradicional con ingredientes locales, recetas prehispánicas y procesos artesanales como el pan de pulque y el destilado de agave. Cada platillo es una experiencia sensorial que conecta con nuestras raíces.',
                'boton_texto': 'Conoce más',
                'boton_url': '#',
                'imagen_1': 'img/about/comida1.png',
                'imagen_2': 'img/about/comida2.png',
                'layout': 'images-left-text-right',
                'fondo_color': '#fafafa'
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✓ Gastronomía Ancestral creado'))

        # Sección 6: Reservaciones
        Seccion.objects.create(
            pagina=home,
            tipo='cta',
            titulo='Elige tu experiencia',
            orden=6,
            activa=True,
            configuracion={
                'subtitulo': 'Reservaciones',
                'titulo': 'Elige tu experiencia',
                'items': [
                    {
                        'titulo': 'Hospedaje',
                        'subtitulo': '¡Descansa en la naturaleza!',
                        'imagen': 'img/rooms/hospedaje.jpg',
                        'boton_texto': 'Reservar',
                        'boton_url': '{% url "reservacion_hospedaje" %}'
                    },
                    {
                        'titulo': 'Experiencia Mágica',
                        'subtitulo': 'Conoce, saborea y vive Xoletongo',
                        'imagen': 'img/rooms/experiencia.jpg',
                        'boton_texto': 'Reservar',
                        'boton_url': '{% url "experiencia" %}'
                    },
                    {
                        'titulo': 'Temporada de Luciérnagas',
                        'subtitulo': 'Disponible de junio a agosto',
                        'imagen': 'img/rooms/luciernagas.jpg',
                        'boton_texto': 'Reservar',
                        'boton_url': '{% url "luciernagas_hospedaje" %}'
                    }
                ],
                'fondo_oscuro': True
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✓ Sección Reservaciones creado'))

        # Sección 7: CTA Contact
        Seccion.objects.create(
            pagina=home,
            tipo='cta',
            titulo='Contacto WhatsApp',
            orden=7,
            activa=True,
            configuracion={
                'titulo': '¿Tienes alguna pregunta? ¡Contáctanos!',
                'tipo': 'whatsapp',
                'telefono': '+52 748 106 5103',
                'url': 'https://wa.me/5211234567890'
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✓ CTA Contact creado'))

        # ====== CREAR PÁGINAS VACÍAS PARA OTRAS SECCIONES ======
        for slug, titulo in [('servicios', 'Servicios'), ('nosotros', 'Nosotros'), 
                             ('galeria', 'Galería'), ('contacto', 'Contacto')]:
            pagina = Pagina.objects.create(
                empresa=xoletongo,
                slug=slug,
                titulo=titulo,
                activa=True
            )
            self.stdout.write(self.style.SUCCESS(f'📄 Página "{titulo}" creada (sin secciones por ahora)'))

        self.stdout.write(self.style.SUCCESS('\n✅ ¡Migración completada exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'   Total de páginas creadas: {Pagina.objects.filter(empresa=xoletongo).count()}'))
        self.stdout.write(self.style.SUCCESS(f'   Total de secciones creadas: {Seccion.objects.filter(pagina__empresa=xoletongo).count()}'))

