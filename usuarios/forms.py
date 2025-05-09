from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'nombre_completo', 'email', 'fecha_nacimiento', 'telefono', 'password1', 'password2']
