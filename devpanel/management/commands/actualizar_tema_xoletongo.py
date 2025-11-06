# devpanel/management/commands/actualizar_tema_xoletongo.py
from django.core.management.base import BaseCommand
from empresas.models import Empresa, Tema

class Command(BaseCommand):
    help = 'Actualiza el tema de Xoletongo con sus colores originales'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎨 Actualizando tema de Xoletongo...'))
        
        try:
            # Obtener la empresa Xoletongo
            xoletongo = Empresa.objects.get(nombre='Xoletongo')
            
            # Obtener o crear el tema "Xoletongo Verde"
            tema, created = Tema.objects.get_or_create(
                nombre='Xoletongo Verde',
                defaults={
                    'color_primario': '#689F38',     # Verde más oscuro para navbar
                    'color_secundario': '#8BC34A',   # Verde medio
                    'color_acento': '#8dd34d',       # Verde brillante (botones, hover)
                    'color_texto': '#333333',        # Gris oscuro
                    'color_fondo': '#FFFFFF',        # Blanco
                    'fuente_principal': 'Roboto',
                    'fuente_secundaria': 'Open Sans',
                    'estilo_layout': 'moderno',
                    'navbar_estilo': 'transparente_scroll',  # Navbar transparente
                    'activo': True,
                }
            )
            
            if not created:
                # Actualizar colores si ya existía
                tema.color_primario = '#689F38'
                tema.color_secundario = '#8BC34A'
                tema.color_acento = '#8dd34d'
                tema.color_texto = '#333333'
                tema.color_fondo = '#FFFFFF'
                tema.navbar_estilo = 'transparente_scroll'
                tema.activo = True
                tema.save()
                self.stdout.write(self.style.SUCCESS('  ✓ Tema actualizado'))
            else:
                self.stdout.write(self.style.SUCCESS('  ✓ Tema creado'))
            
            # Asignar el tema a Xoletongo
            xoletongo.tema = tema
            xoletongo.save()
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Tema de Xoletongo configurado exitosamente'))
            self.stdout.write(self.style.SUCCESS(f'   Color primario: {tema.color_primario}'))
            self.stdout.write(self.style.SUCCESS(f'   Color acento: {tema.color_acento}'))
            self.stdout.write(self.style.SUCCESS(f'   Navbar: Transparente con scroll'))
            
        except Empresa.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Empresa Xoletongo no encontrada'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))

