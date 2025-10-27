# adminpanel/utils.py
from .models import Novedad

def registrar_novedad(usuario, accion):
    Novedad.objects.create(usuario=usuario, accion=accion)
