# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0006_remove_customuser_rol_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='rol_nuevo',
            new_name='rol',
        ),
    ]

