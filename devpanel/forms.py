# devpanel/forms.py
from django import forms
from empresas.models import Empresa
from .models import CustomAttribute

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nombre', 'activa']
        labels = {
            'nombre': 'Nombre de la Empresa',
            'activa': '¿Activar esta empresa al crearla?',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CustomAttributeForm(forms.ModelForm):
    class Meta:
        model = CustomAttribute
        # El campo 'empresa' lo asignaremos automáticamente en la vista
        fields = ['target_model', 'name', 'attribute_type']
        labels = {
            'target_model': 'Modelo de Destino',
            'name': 'Nombre del Atributo (ej. Talla, Autor)',
            'attribute_type': 'Tipo de Dato',
        }
        widgets = {
            'target_model': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'attribute_type': forms.Select(attrs={'class': 'form-control'}),
        }