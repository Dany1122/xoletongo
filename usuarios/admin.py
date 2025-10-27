from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Los campos a mostrar en la lista de usuarios
    list_display = ['username', 'email', 'nombre_completo', 'get_rol_display', 'empresa', 'is_staff']

    # Campos en la página para EDITAR un usuario
    fieldsets = UserAdmin.fieldsets + (

        ('Campos Personalizados', {
            'fields': ('nombre_completo', 'fecha_nacimiento', 'telefono', 'rol_legacy', 'rol_nuevo', 'atributos_personalizados', 'empresa'),
        }),
    )

    # Campos en la página para CREAR un usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Campos Personalizados', {
            'fields': ('nombre_completo', 'fecha_nacimiento', 'telefono', 'rol_legacy', 'rol_nuevo', 'atributos_personalizados', 'empresa'),
        }),
    )
    
    def get_rol_display(self, obj):
        """Muestra el rol del usuario (compatible con ambos sistemas)"""
        return obj.get_rol_nombre()
    get_rol_display.short_description = 'Rol'

admin.site.register(CustomUser, CustomUserAdmin)
