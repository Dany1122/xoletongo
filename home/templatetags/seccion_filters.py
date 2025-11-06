from django import template
from django.urls import reverse, NoReverseMatch
import re

register = template.Library()

@register.filter(name='resolve_url')
def resolve_url(url_string):
    """
    Intenta resolver URLs que contienen template tags como {% url 'nombre' %}
    Si no puede, devuelve la URL tal cual
    """
    if not url_string:
        return '#'
    
    # Buscar patrón {% url 'nombre' %}
    match = re.search(r"{%\s*url\s+'([^']+)'\s*%}", url_string)
    if match:
        url_name = match.group(1)
        try:
            return reverse(url_name)
        except NoReverseMatch:
            return '#'
    
    # Si no es un template tag, devolver tal cual
    return url_string

