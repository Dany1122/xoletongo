# Generated by Django 5.2 on 2025-06-06 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservaciones', '0011_alter_reservacion_empresa'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservacion',
            name='hora_recepcion',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reservacion',
            name='fecha_inicio',
            field=models.DateField(blank=True, null=True),
        ),
    ]
