# devpanel/forms.py
from django import forms
from empresas.models import Empresa
from .models import CustomAttribute, Seccion, Pagina
import json

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


class SeccionBaseForm(forms.ModelForm):
    """Formulario base para crear una nueva sección (solo tipo y título)"""
    class Meta:
        model = Seccion
        fields = ['tipo', 'titulo', 'activa']
        labels = {
            'tipo': 'Tipo de Sección',
            'titulo': 'Título identificador (opcional)',
            'activa': 'Activar sección',
        }
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Banner principal, Servicios, etc.'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SeccionConfigForm(forms.Form):
    """Formulario dinámico para editar la configuración JSON de una sección"""
    configuracion_json = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 20,
            'style': 'font-family: monospace;'
        }),
        label='Configuración JSON',
        help_text='Edita la configuración en formato JSON'
    )
    
    def __init__(self, *args, **kwargs):
        seccion = kwargs.pop('seccion', None)
        super().__init__(*args, **kwargs)
        
        if seccion and seccion.configuracion:
            # Pre-llenar con la configuración actual formateada
            self.fields['configuracion_json'].initial = json.dumps(
                seccion.configuracion, 
                indent=2, 
                ensure_ascii=False
            )
    
    def clean_configuracion_json(self):
        """Validar que el JSON sea válido"""
        data = self.cleaned_data['configuracion_json']
        try:
            parsed = json.loads(data)
            return parsed
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f'JSON inválido: {e}')