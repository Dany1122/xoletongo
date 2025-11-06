from django.core.management.base import BaseCommand
from empresas.models import Empresa


class Command(BaseCommand):
    help = 'Habilita el módulo de productos para la empresa Xoletongo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🔧 Habilitando módulo de productos para Xoletongo...'))
        
        try:
            # Buscar empresa Xoletongo
            empresa = Empresa.objects.filter(nombre__icontains='Xoletongo').first()
            
            if not empresa:
                self.stdout.write(self.style.ERROR('❌ No se encontró la empresa Xoletongo'))
                return
            
            # Habilitar productos
            empresa.productos_habilitado = True
            empresa.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Módulo de productos habilitado para {empresa.nombre}'))
            self.stdout.write(self.style.SUCCESS('   - Link "Productos" visible en navbar'))
            self.stdout.write(self.style.SUCCESS('   - Carrito de compras visible'))
            self.stdout.write(self.style.SUCCESS('   - Clientes pueden hacer pedidos'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))

