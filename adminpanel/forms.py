from django import forms
from usuarios.models import CustomUser

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'rol', 'is_active', 'is_staff']
