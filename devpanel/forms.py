# devpanel/forms.py
from django import forms
from empresas.models import Empresa, Tema
from .models import CustomAttribute, Seccion, Pagina, Rol
from usuarios.models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
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


# ==================== FORMULARIO PARA AJUSTES GRÁFICOS ====================

class TemaForm(forms.ModelForm):
    """Formulario para editar el tema visual de la empresa"""
    
    class Meta:
        model = Tema
        fields = [
            'nombre',
            'color_primario',
            'color_secundario',
            'color_acento',
            'color_texto',
            'color_fondo',
            'fuente_principal',
            'fuente_secundaria',
            'navbar_estilo',
            'logo_header',
            'favicon',
            'imagen_hero',
            'activo',
        ]
        labels = {
            'nombre': 'Nombre del Tema',
            'color_primario': 'Color Primario (navbar, títulos)',
            'color_secundario': 'Color Secundario',
            'color_acento': 'Color de Acento (botones, enlaces)',
            'color_texto': 'Color del Texto',
            'color_fondo': 'Color de Fondo',
            'fuente_principal': 'Fuente Principal',
            'fuente_secundaria': 'Fuente Secundaria',
            'navbar_estilo': 'Estilo de Barra de Navegación',
            'logo_header': 'Logo del Header',
            'favicon': 'Favicon (16x16 o 32x32 px)',
            'imagen_hero': 'Imagen Hero/Banner',
            'activo': 'Tema activo',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Tema Principal'
            }),
            'color_primario': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Elige el color primario'
            }),
            'color_secundario': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Elige el color secundario'
            }),
            'color_acento': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Elige el color de acento'
            }),
            'color_texto': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Elige el color del texto'
            }),
            'color_fondo': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'Elige el color de fondo'
            }),
            'fuente_principal': forms.Select(attrs={'class': 'form-control'}),
            'fuente_secundaria': forms.Select(attrs={'class': 'form-control'}),
            'navbar_estilo': forms.RadioSelect(),
            'logo_header': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
            'favicon': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/x-icon,image/png'
            }),
            'imagen_hero': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'color_primario': 'Usado en navbar, encabezados y elementos principales',
            'color_acento': 'Usado en botones, enlaces y llamados a la acción',
            'favicon': 'Icono que aparece en la pestaña del navegador',
            'logo_header': 'Logo que aparece en el header de la página',
        }


# ==================== FORMULARIOS PARA GESTIÓN DE STAFF ====================

class SuperuserForm(forms.ModelForm):
    """Formulario para crear superusuarios (staff del DevPanel)"""
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Mínimo 8 caracteres. Debe incluir letras y números. No puede ser demasiado común.'
    )
    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Email',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'is_active': 'Activo',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'usuario_admin'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'admin@ejemplo.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Juan'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pérez'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        
        if password and password_confirm:
            # Verificar que coincidan
            if password != password_confirm:
                self.add_error('password_confirm', 'Las contraseñas no coinciden.')
            else:
                # Usar validadores de Django para seguridad robusta
                try:
                    # Crear un objeto temporal para validar contra atributos del usuario
                    user_temp = CustomUser(username=username, email=email)
                    validate_password(password, user=user_temp)
                except ValidationError as e:
                    # Agregar todos los errores de validación
                    for error in e.messages:
                        self.add_error('password', error)
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_superuser = True
        user.is_staff = True
        user.empresa = None  # Staff no pertenece a ninguna empresa
        user.rol = None  # Staff no tiene rol
        
        if commit:
            user.save()
        
        return user


class SuperuserEditForm(forms.ModelForm):
    """Formulario para editar superusuarios existentes"""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Email',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'is_active': 'Activo',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }