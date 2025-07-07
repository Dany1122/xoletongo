from django import forms
from usuarios.models import CustomUser

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
    
class CustomUserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'telefono', 'rol', 'is_active']