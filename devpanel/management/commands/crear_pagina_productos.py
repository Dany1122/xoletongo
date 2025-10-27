from django.core.management.base import BaseCommand
from devpanel.models import Pagina, Seccion, Rol
from empresas.models import Empresa


class Command(BaseCommand):
    help = 'Crea la página de Productos en el devpanel con secciones de ejemplo'

    def handle(self, *args, **kwargs):
        empresa = Empresa.objects.filter(activa=True).first()
        
        if not empresa:
            self.stdout.write(self.style.ERROR('No hay una empresa activa'))
            return
        
        # Crear o obtener la página de productos
        pagina, created = Pagina.objects.get_or_create(
            slug='productos',
            empresa=empresa,
            defaults={
                'titulo': 'Productos',
                'activa': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Página "productos" creada'))
        else:
            self.stdout.write(self.style.WARNING('La página "productos" ya existe'))
        
        # Verificar si ya tiene secciones
        secciones_existentes = Seccion.objects.filter(pagina=pagina).count()
        
        if secciones_existentes == 0:
            # Crear sección Hero de ejemplo
            seccion_hero = Seccion.objects.create(
                pagina=pagina,
                tipo='hero',
                titulo='Hero Productos',
                orden=1,
                activa=True,
                configuracion={
                    'titulo': 'Nuestros Productos',
                    'subtitulo': 'Descubre nuestra selección de productos artesanales y naturales',
                    'opacidad': 0.4
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  ✓ Sección Hero creada'))
            
            # Crear sección de texto de ejemplo
            seccion_texto = Seccion.objects.create(
                pagina=pagina,
                tipo='texto',
                titulo='Texto Calidad',
                orden=100,  # Orden alto para que aparezca al final
                activa=True,
                configuracion={
                    'titulo': 'Calidad Garantizada',
                    'contenido': 'Todos nuestros productos son elaborados con ingredientes naturales y tradicionales de la región.'
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  ✓ Sección de texto creada'))
            
            self.stdout.write(self.style.SUCCESS(
                '\n✓ ¡Página de productos configurada correctamente!\n'
                'Puedes personalizar las secciones desde el devpanel.'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'La página ya tiene {secciones_existentes} secciones configuradas.'
            ))

