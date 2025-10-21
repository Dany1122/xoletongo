# devpanel/forms.py
from django import forms
from empresas.models import Empresa
from .models import CustomAttribute, Seccion, Pagina, Rol
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


# ==================== FORMULARIOS PARA ROLES ====================

class RolForm(forms.ModelForm):
    """Formulario para crear/editar roles"""
    class Meta:
        model = Rol
        fields = ['nombre', 'descripcion', 'activo']
        labels = {
            'nombre': 'Nombre del Rol',
            'descripcion': 'Descripción',
            'activo': 'Rol activo',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Guía Turístico, Chef, Contador'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe las responsabilidades de este rol...'
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    def __init__(self, *args, **kwargs):
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
    def clean_nombre(self):
        """Validar que el nombre del rol sea único dentro de la empresa"""
        nombre = self.cleaned_data['nombre'].strip()
        
        # Filtrar por empresa
        queryset = Rol.objects.filter(nombre__iexact=nombre)
        
        # Excluir la instancia actual si es una edición
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        # Filtrar por empresa
        if self.empresa:
            queryset = queryset.filter(empresa=self.empresa)
        
        if queryset.exists():
            raise forms.ValidationError("Ya existe un rol con ese nombre en esta empresa.")
        
        return nombre


class AtributoSchemaForm(forms.Form):
    """Formulario para agregar un atributo al schema de un rol"""
    TIPO_CHOICES = [
        ('texto', 'Texto'),
        ('numero', 'Número'),
        ('email', 'Email'),
        ('telefono', 'Teléfono'),
        ('fecha', 'Fecha'),
        ('booleano', 'Sí/No'),
        ('seleccion', 'Selección (lista)'),
        ('texto_largo', 'Texto largo'),
    ]
    
    nombre = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Certificación, Idiomas, RFC'
        }),
        label='Nombre del campo'
    )
    
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de dato'
    )
    
    requerido = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Campo obligatorio'
    )
    
    opciones = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Separadas por comas: Español, Inglés, Francés'
        }),
        label='Opciones (solo para tipo "Selección")',
        help_text='Ingresa las opciones separadas por comas'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        opciones = cleaned_data.get('opciones')
        
        # Si es tipo selección, las opciones son obligatorias
        if tipo == 'seleccion' and not opciones:
            raise forms.ValidationError('Debes especificar opciones para el tipo "Selección"')
        
        return cleaned_data