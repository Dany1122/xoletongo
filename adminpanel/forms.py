from django import forms
from usuarios.models import CustomUser
from servicios.models import Servicio, TipoServicio, ImagenServicio
from empresas.models import Empresa
from django.forms import inlineformset_factory
from devpanel.models import CustomAttribute

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
                  'restricciones'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'servicio': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'costo_por_persona': forms.NumberInput(attrs={'class': 'form-control'}),
            'costo_niño': forms.NumberInput(attrs={'class': 'form-control'}),
            'costo_con_descuento': forms.NumberInput(attrs={'class': 'form-control'}),
            'imagen_principal': forms.FileInput(attrs={'class': 'form-control-file'}),
            'duracion': forms.NumberInput(attrs={'class': 'form-control'}),
            'restricciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        # Extraemos la 'empresa' que pasaremos desde la vista
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        self.custom_fields = []  # Guardaremos los nombres de los campos personalizados aquí

        if self.empresa:
            # Buscamos todos los atributos definidos para el modelo 'Servicio' de esta empresa
            custom_attributes = CustomAttribute.objects.filter(
                empresa=self.empresa, 
                target_model='Servicio'
            )

            # Creamos un campo de formulario para cada atributo definido
            for attr in custom_attributes:
                field_name = f'custom_{attr.name.lower().replace(" ", "_")}'
                self.custom_fields.append(field_name)
                
                # Asignamos el valor inicial si estamos editando un servicio
                initial_value = None
                if self.instance and self.instance.pk and self.instance.atributos_personalizados:
                    initial_value = self.instance.atributos_personalizados.get(attr.name)

                # Creamos el tipo de campo correcto
                if attr.attribute_type == 'TEXT':
                    self.fields[field_name] = forms.CharField(
                        label=attr.name, 
                        required=False, 
                        initial=initial_value, 
                        widget=forms.TextInput(attrs={'class': 'form-control'})
                    )
                elif attr.attribute_type == 'NUMBER':
                    self.fields[field_name] = forms.IntegerField(
                        label=attr.name, 
                        required=False, 
                        initial=initial_value, 
                        widget=forms.NumberInput(attrs={'class': 'form-control'})
                    )
                elif attr.attribute_type == 'TEXTAREA':
                    self.fields[field_name] = forms.CharField(
                        label=attr.name, 
                        required=False, 
                        initial=initial_value, 
                        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
                    )
                elif attr.attribute_type == 'DATE':
                    self.fields[field_name] = forms.DateField(
                        label=attr.name, 
                        required=False, 
                        initial=initial_value, 
                        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
                    )
                elif attr.attribute_type == 'BOOLEAN':
                    self.fields[field_name] = forms.BooleanField(
                        label=attr.name, 
                        required=False, 
                        initial=initial_value, 
                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
                    )

    def save(self, commit=True):
        # Crear la instancia del servicio en memoria SIN guardarla en la BD todavía
        instance = super().save(commit=False)
        
        if self.empresa:
            instance.empresa = self.empresa

        # Recopilar los atributos personalizados
        custom_data = {}
        for attr in CustomAttribute.objects.filter(empresa=instance.empresa, target_model='Servicio'):
            field_name = f'custom_{attr.name.lower().replace(" ", "_")}'
            # Obtener el valor del formulario
            custom_data[attr.name] = self.cleaned_data.get(field_name)
        
        # Asignar los datos personalizados al JSONField
        instance.atributos_personalizados = custom_data
        
        # Guardar si commit es True
        if commit:
            instance.save()
            
        return instance

    
class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'telefono', 'rol', 'is_active']


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
    
from django import forms
from .models import Producto, CategoriaProducto

class ProductoForm(forms.ModelForm):
    # Campos base que no cambian
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'categoria', 'perecedero', 
                  'fecha_caducidad', 'stock', 'sku', 'activo', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'perecedero': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_caducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        # 1. Extraemos la 'empresa' que pasaremos desde la vista
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        self.custom_fields = [] # Guardaremos los nombres de los campos personalizados aquí

        if self.empresa:
            # 2. Buscamos todos los atributos definidos para el modelo 'Producto' de esta empresa
            custom_attributes = CustomAttribute.objects.filter(
                empresa=self.empresa, 
                target_model='Producto'
            )

            # 3. Creamos un campo de formulario para cada atributo definido
            for attr in custom_attributes:
                field_name = f'custom_{attr.name.lower().replace(" ", "_")}'
                self.custom_fields.append(field_name)
                
                # Asignamos el valor inicial si estamos editando un producto
                initial_value = None
                if self.instance and self.instance.pk and self.instance.atributos_personalizados:
                    initial_value = self.instance.atributos_personalizados.get(attr.name)

                # Creamos el tipo de campo correcto
                if attr.attribute_type == 'TEXT':
                    self.fields[field_name] = forms.CharField(label=attr.name, required=False, initial=initial_value, widget=forms.TextInput(attrs={'class': 'form-control'}))
                elif attr.attribute_type == 'NUMBER':
                    self.fields[field_name] = forms.IntegerField(label=attr.name, required=False, initial=initial_value, widget=forms.NumberInput(attrs={'class': 'form-control'}))
                elif attr.attribute_type == 'TEXTAREA':
                    self.fields[field_name] = forms.CharField(label=attr.name, required=False, initial=initial_value, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
                # Puedes añadir más tipos aquí (DATE, BOOLEAN, etc.)

    def save(self, commit=True):
        # 1. Create the product instance in memory WITHOUT saving it to the DB yet.
        # The view will have already assigned the empresa to this instance.
        instance = super().save(commit=False)
        
        if self.empresa:
            instance.empresa = self.empresa


        # 2. Now that we have the instance and its company, gather the custom attributes.
        custom_data = {}
        for attr in CustomAttribute.objects.filter(empresa=instance.empresa, target_model='Producto'):
            field_name = f'custom_{attr.name.lower().replace(" ", "_")}'
            # Get the value from the form's cleaned data
            custom_data[attr.name] = self.cleaned_data.get(field_name)
        
        # 3. Assign the collected custom data to the JSONField.
        instance.atributos_personalizados = custom_data
        
        # 4. If commit is True, save the completed instance to the database.
        if commit:
            instance.save()
            # self.save_m2m() # Use this if you have many-to-many fields
            
        return instance

class CategoriaProductoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProducto
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TipoServicioForm(forms.ModelForm):
    class Meta:
        model = TipoServicio
        fields = ["nombre", "descripcion", "tipo"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "tipo": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        # Verificar duplicados solo en la misma empresa
        queryset = TipoServicio.objects.filter(nombre__iexact=nombre)
        
        # Si estamos editando, excluir el registro actual
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        # Filtrar por empresa si está disponible
        if self.empresa:
            queryset = queryset.filter(empresa=self.empresa)
        
        if queryset.exists():
            raise forms.ValidationError("Ya existe un tipo de servicio con ese nombre en esta empresa.")
        return nombre
    
    
ImagenFormSet = inlineformset_factory(
    Servicio,
    ImagenServicio,
    fields=("imagen", "descripcion", "orden"),
    widgets={
        "imagen": forms.ClearableFileInput(attrs={"class": "form-control-file"}),
        "descripcion": forms.TextInput(attrs={"class": "form-control"}),
        "orden": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
    },
    extra=3,          # número inicial de filas vacías
    can_delete=True,  # permitir eliminar imágenes existentes
)