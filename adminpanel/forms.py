from django import forms
from usuarios.models import CustomUser
from servicios.models import Servicio
from empresas.models import Empresa

class CustomUserForm(forms.ModelForm):
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
    )
    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput,
    )
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'rol', 'is_active', 'telefono']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

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

    
    
class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'telefono', 'rol', 'is_active']

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


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = [
            "nombre", "nombre_titular", "correo_contacto", "telefono", "ubicacion",
            "cuenta_bancaria", "clabe", "numero_terjeta", "logotipo", "sitio_web",
            "activa", "smtp_host", "smtp_port", "smtp_user", "smtp_password",
            "smtp_use_tls", "smtp_use_ssl",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "nombre_titular": forms.TextInput(attrs={"class": "form-control"}),
            "correo_contacto": forms.EmailInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control"}),
            "ubicacion": forms.TextInput(attrs={"class": "form-control"}),
            "cuenta_bancaria": forms.TextInput(attrs={"class": "form-control", "maxlength": 18}),
            "clabe": forms.TextInput(attrs={"class": "form-control", "maxlength": 18}),
            "numero_terjeta": forms.TextInput(attrs={"class": "form-control", "maxlength": 16}),
            "sitio_web": forms.URLInput(attrs={"class": "form-control"}),
            "activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "smtp_host": forms.TextInput(attrs={"class": "form-control"}),
            "smtp_port": forms.NumberInput(attrs={"class": "form-control"}),
            "smtp_user": forms.TextInput(attrs={"class": "form-control"}),
            "smtp_password": forms.PasswordInput(render_value=True, attrs={"class": "form-control"}),
            "smtp_use_tls": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "smtp_use_ssl": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        data = super().clean()
        # Evitar TLS y SSL a la vez
        if data.get("smtp_use_tls") and data.get("smtp_use_ssl"):
            self.add_error("smtp_use_ssl", "No puedes activar TLS y SSL al mismo tiempo.")
        return data