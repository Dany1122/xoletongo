from django import forms
from usuarios.models import CustomUser
from servicios.models import Servicio

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 
                  'email', 
                  'rol', 
                  'is_active', 
                  'is_staff']

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['titulo', 
                  'servicio', 
                  'descripcion', 
                  'costo_por_persona',
                  'costo_niño', 
                  'costo_con_descuento', 
                  'imagen_principal',
                  'duracion', 
                  'restricciones', 
                  'galeria'
        ]