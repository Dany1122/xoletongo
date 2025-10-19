from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Los campos a mostrar en la lista de usuarios
    list_display = ['username', 'email', 'nombre_completo', 'rol', 'empresa', 'is_staff']

    # Campos en la página para EDITAR un usuario
    fieldsets = UserAdmin.fieldsets + (

        ('Campos Personalizados', {
            'fields': ('nombre_completo', 'fecha_nacimiento', 'telefono', 'rol', 'empresa'),
        }),
    )

    # Campos en la página para CREAR un usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Campos Personalizados', {
            'fields': ('nombre_completo', 'fecha_nacimiento', 'telefono', 'rol', 'empresa'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)