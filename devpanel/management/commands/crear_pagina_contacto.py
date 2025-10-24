from django.core.management.base import BaseCommand
from devpanel.models import Pagina, Seccion
from empresas.models import Empresa

class Command(BaseCommand):
    help = 'Crea la página "contacto" en el devpanel con secciones de ejemplo si no existe.'

    def handle(self, *args, **options):
        empresa = Empresa.objects.filter(activa=True).first()

        if not empresa:
            self.stdout.write(self.style.ERROR('No hay una empresa activa'))
            return

        # Crear o obtener la página de contacto
        pagina, created = Pagina.objects.get_or_create(
            slug='contacto',
            empresa=empresa,
            defaults={
                'titulo': 'Contacto',
                'activa': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Página "contacto" creada'))
        else:
            self.stdout.write(self.style.WARNING('La página "contacto" ya existe'))

        # Verificar si ya tiene secciones
        secciones_existentes = Seccion.objects.filter(pagina=pagina).count()

        if secciones_existentes == 0:
            # Crear sección de Formulario de Contacto
            Seccion.objects.create(
                pagina=pagina,
                tipo='contacto_form',
                titulo='Formulario de Contacto',
                orden=1,
                activa=True,
                configuracion={
                    'titulo': 'Contáctanos',
                    'texto_boton': 'Enviar Mensaje',
                    'boton_bg_color': '#007bff',
                    'boton_text_color': '#ffffff',
                    'boton_hover_color': '#0056b3',
                    'campos': [
                        {
                            'nombre': 'nombre',
                            'tipo': 'text',
                            'placeholder': 'Ingresa tu nombre',
                            'requerido': True,
                            'columnas': 6
                        },
                        {
                            'nombre': 'email',
                            'tipo': 'email',
                            'placeholder': 'Tu correo electrónico',
                            'requerido': True,
                            'columnas': 6
                        },
                        {
                            'nombre': 'asunto',
                            'tipo': 'text',
                            'placeholder': 'Asunto del mensaje',
                            'requerido': True,
                            'columnas': 12
                        },
                        {
                            'nombre': 'mensaje',
                            'tipo': 'textarea',
                            'placeholder': 'Escribe tu mensaje aquí...',
                            'requerido': True,
                            'filas': 9
                        }
                    ],
                    'info_contacto': [
                        {
                            'icono': 'ti-home',
                            'titulo': 'Dirección',
                            'contenido': 'Carretera Miguel Lira Y Ortega, Santa Cruz Moxolahua Km 1.5'
                        },
                        {
                            'icono': 'ti-tablet',
                            'titulo': 'Teléfono',
                            'contenido': '+52 123 456 7890'
                        },
                        {
                            'icono': 'ti-email',
                            'titulo': 'Email',
                            'contenido': 'info@xoletongo.com'
                        }
                    ]
                }
            )
            self.stdout.write(self.style.SUCCESS(f'  ✓ Sección de Formulario creada'))

            self.stdout.write(self.style.SUCCESS(
                '\n✓ ¡Página de contacto configurada correctamente!\n'
                'Puedes personalizar los campos desde el devpanel.'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'La página ya tiene {secciones_existentes} secciones configuradas.'
            ))

