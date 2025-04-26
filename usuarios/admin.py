from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'nombre_completo', 'fecha_nacimiento', 'telefono', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('nombre_completo', 'fecha_nacimiento', 'telefono')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('nombre_completo', 'fecha_nacimiento', 'telefono')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
