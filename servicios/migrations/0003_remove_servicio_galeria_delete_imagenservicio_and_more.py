# Generated by Django 5.2 on 2025-04-18 03:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicios', '0002_rename_titulo_servicio_tituloo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='servicio',
            name='galeria',
        ),
        migrations.DeleteModel(
            name='ImagenServicio',
        ),
        migrations.DeleteModel(
            name='Servicio',
        ),
    ]
