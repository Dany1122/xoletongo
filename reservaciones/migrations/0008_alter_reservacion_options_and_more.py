# Generated by Django 5.2 on 2025-05-11 21:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservaciones', '0007_merge_20250511_1532'),
        ('servicios', '0013_tiposervicio_descripcion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reservacion',
            options={},
        ),
        migrations.AlterField(
            model_name='reservacion_servicio',
            name='id_reservacion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservacion', to='reservaciones.reservacion'),
        ),
        migrations.AlterField(
            model_name='reservacion_servicio',
            name='servicio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tipoServicio', to='servicios.servicio'),
        ),
    ]
