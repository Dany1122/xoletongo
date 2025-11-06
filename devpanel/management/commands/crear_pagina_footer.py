from django.core.management.base import BaseCommand
from devpanel.models import Pagina, Seccion
from empresas.models import Empresa


class Command(BaseCommand):
    help = 'Crea la página "footer" en el devpanel con secciones de ejemplo si no existe.'

    def handle(self, *args, **options):
        empresa = Empresa.objects.filter(activa=True).first()

        if not empresa:
            self.stdout.write(self.style.ERROR('No hay una empresa activa'))
            return

        # Crear o obtener la página del footer
        pagina, created = Pagina.objects.get_or_create(
            slug='footer',
            empresa=empresa,
            defaults={
                'titulo': 'Footer',
                'activa': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Página "footer" creada'))
        else:
            self.stdout.write(self.style.WARNING('La página "footer" ya existe'))

        # Verificar si ya tiene secciones
        secciones_existentes = Seccion.objects.filter(pagina=pagina).count()

        if secciones_existentes == 0:
            # Crear sección de Mapa
            seccion_mapa = Seccion.objects.create(
                pagina=pagina,
                tipo='mapa',
                titulo='Ubicación',
                orden=1,
                activa=True,
                configuracion={
                    'titulo': 'Ubicación',
                    'direccion': 'Carretera Miguel Lira Y Ortega\nSanta Cruz Moxolahua Km 1.5',
                    'iframe_url': 'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3874.3455951249916!2d-98.54644622473863!3d19.46889383952075!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x85d1d147b7c8f5f9%3A0x8bdf72377f84c714!2sxoletongo%20centro%20de%20avistamiento!5e1!3m2!1ses-419!2smx!4v1744858078568!5m2!1ses-419!2smx',
                    'ancho': '100%',
                    'alto': '450'
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  ✓ Sección Mapa creada'))

            # Crear sección de Galería
            seccion_galeria = Seccion.objects.create(
                pagina=pagina,
                tipo='galeria',
                titulo='Galería Footer',
                orden=2,
                activa=True,
                configuracion={
                    'titulo': 'Galería',
                    'columnas': 2,
                    'imagenes': [
                        {'url': 'img/gallery/1.jpg', 'alt': 'Imagen 1'},
                        {'url': 'img/gallery/2.jpg', 'alt': 'Imagen 2'},
                        {'url': 'img/gallery/3.jpg', 'alt': 'Imagen 3'},
                        {'url': 'img/gallery/4.jpg', 'alt': 'Imagen 4'}
                    ]
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  ✓ Sección Galería creada'))

            # Crear sección de Copyright
            seccion_copyright = Seccion.objects.create(
                pagina=pagina,
                tipo='texto',
                titulo='Copyright',
                orden=3,
                activa=True,
                configuracion={
                    'contenido': '&copy; Xoletongo - Todos los derechos reservados.',
                    'alineacion': 'center',
                    'texto_color': '#ffffff'
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  ✓ Sección Copyright creada'))

            self.stdout.write(self.style.SUCCESS(
                '\n✓ ¡Página de footer configurada correctamente!\n'
                'Puedes personalizar las secciones desde el devpanel.'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'La página ya tiene {secciones_existentes} secciones configuradas.'
            ))

