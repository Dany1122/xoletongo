from django.core.management.base import BaseCommand
from empresas.models import Empresa
from devpanel.models import Rol
from usuarios.models import CustomUser


class Command(BaseCommand):
    help = 'Migra los roles legacy (CharField) al nuevo sistema de roles dinámicos (ForeignKey)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔄 Iniciando migración de roles legacy...'))

        # Obtener todas las empresas
        empresas = Empresa.objects.all()
        
        if not empresas.exists():
            self.stderr.write(self.style.ERROR('❌ No hay empresas registradas'))
            return

        # Roles por defecto que existían
        roles_legacy = [
            {
                'nombre': 'Administrador',
                'descripcion': 'Usuario con permisos completos de administración del sistema',
                'atributos_schema': [
                    {
                        'nombre': 'Nivel',
                        'tipo': 'lista',
                        'opciones': ['Senior', 'Mid', 'Junior'],
                        'requerido': False
                    },
                    {
                        'nombre': 'Departamento',
                        'tipo': 'texto',
                        'requerido': False
                    }
                ]
            },
            {
                'nombre': 'Empleado',
                'descripcion': 'Personal operativo de la empresa',
                'atributos_schema': [
                    {
                        'nombre': 'Turno',
                        'tipo': 'lista',
                        'opciones': ['Matutino', 'Vespertino', 'Mixto'],
                        'requerido': False
                    },
                    {
                        'nombre': 'Área',
                        'tipo': 'texto',
                        'requerido': False
                    }
                ]
            },
            {
                'nombre': 'Encargado',
                'descripcion': 'Supervisor o jefe de área',
                'atributos_schema': [
                    {
                        'nombre': 'Área Responsable',
                        'tipo': 'texto',
                        'requerido': False
                    }
                ]
            },
            {
                'nombre': 'Cliente',
                'descripcion': 'Usuario registrado del sistema',
                'atributos_schema': [
                    {
                        'nombre': 'Tipo Cliente',
                        'tipo': 'lista',
                        'opciones': ['Regular', 'VIP', 'Corporativo'],
                        'requerido': False
                    }
                ]
            }
        ]

        # Crear roles para cada empresa
        roles_creados = {}
        for empresa in empresas:
            self.stdout.write(f'\n📦 Creando roles para: {empresa.nombre}')
            roles_creados[empresa.id] = {}
            
            for rol_data in roles_legacy:
                rol, created = Rol.objects.get_or_create(
                    empresa=empresa,
                    nombre=rol_data['nombre'],
                    defaults={
                        'descripcion': rol_data['descripcion'],
                        'atributos_schema': rol_data['atributos_schema'],
                        'activo': True
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Rol "{rol.nombre}" creado'))
                else:
                    self.stdout.write(f'  → Rol "{rol.nombre}" ya existía')
                
                roles_creados[empresa.id][rol_data['nombre']] = rol

        # Migrar usuarios
        self.stdout.write('\n👥 Migrando usuarios...')
        usuarios = CustomUser.objects.all()
        migrados = 0
        sin_empresa = 0
        
        for usuario in usuarios:
            if usuario.rol_legacy and usuario.empresa:
                # Buscar el rol correspondiente
                rol_nuevo = roles_creados.get(usuario.empresa.id, {}).get(usuario.rol_legacy)
                
                if rol_nuevo:
                    usuario.rol = rol_nuevo
                    usuario.save(update_fields=['rol'])
                    migrados += 1
                    self.stdout.write(f'  ✓ {usuario.username} → {rol_nuevo.nombre}')
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠ {usuario.username}: No se encontró rol "{usuario.rol_legacy}"'))
            elif not usuario.empresa:
                sin_empresa += 1
                self.stdout.write(self.style.WARNING(f'  ⚠ {usuario.username}: Sin empresa asignada'))

        # Resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ MIGRACIÓN COMPLETADA'))
        self.stdout.write('='*60)
        self.stdout.write(f'📊 Roles creados: {sum(len(roles) for roles in roles_creados.values())}')
        self.stdout.write(f'👥 Usuarios migrados: {migrados}')
        if sin_empresa:
            self.stdout.write(self.style.WARNING(f'⚠️  Usuarios sin empresa: {sin_empresa}'))
        self.stdout.write('\n💡 Los usuarios mantienen su rol_legacy por compatibilidad')
        self.stdout.write('💡 Actualiza el AdminPanel para usar rol_nuevo en lugar de rol_legacy')

