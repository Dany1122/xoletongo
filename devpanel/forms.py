# devpanel/forms.py
from django import forms
from empresas.models import Empresa

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