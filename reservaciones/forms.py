from django import forms
from .models import Reservacion

class ReservacionAnonimaForm(forms.ModelForm):
    class Meta:
        model = Reservacion
        fields = [
            'nombre_cliente',
            'email_cliente',
            'fecha_inicio',
            'fecha_fin',
            'numero_personas',
            'comentario',
            'pago_realizado'
        ]

class ReservacionAutenticadaForm(forms.ModelForm):
    class Meta:
        model = Reservacion
        fields = [
            'fecha_inicio',
            'fecha_fin',
            'numero_personas',
            'comentario',
            'pago_realizado'
        ]
