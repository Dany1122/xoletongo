from django import forms
from .models import Resena


class ResenaForm(forms.ModelForm):
    """Formulario para crear reseñas"""
    
    class Meta:
        model = Resena
        fields = ['calificacion', 'comentario']
        widgets = {
            'calificacion': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Comparte tu experiencia...'
            }),
        }
        labels = {
            'calificacion': 'Calificación',
            'comentario': 'Comentario',
        }

