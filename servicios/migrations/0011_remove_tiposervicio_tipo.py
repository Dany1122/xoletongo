# Generated by Django 5.2 on 2025-05-03 04:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicios', '0010_servicio_costo_con_descuento_servicio_costo_niño'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tiposervicio',
            name='tipo',
        ),
    ]
