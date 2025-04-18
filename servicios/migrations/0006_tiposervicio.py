# Generated by Django 5.2 on 2025-04-18 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servicios', '0005_rename_tituloo_servicio_titulo'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoServicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, null=True)),
                ('tipo', models.CharField(choices=[('hospedaje', 'Hospedaje'), ('visita', 'Visita'), ('restaurante', 'Restaurante')], max_length=50)),
            ],
        ),
    ]
