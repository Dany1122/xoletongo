from django import template
import json

register = template.Library()

@register.filter(name='pprint')
def pprint(value):
    """Pretty print JSON data"""
    try:
        return json.dumps(value, indent=2, ensure_ascii=False)
    except:
        return str(value)

@register.simple_tag
def get_model_choices(model_instance, field_name):
    """Obtiene las choices de un campo del modelo"""
    try:
        field = model_instance._meta.get_field(field_name)
        return field.choices
    except:
        return []

