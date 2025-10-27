from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import ImagenServicio
import os

@receiver(post_delete, sender=ImagenServicio)
def borrar_archivo_imagen(sender, instance, **kwargs):
    if instance.imagen and instance.imagen.storage.exists(instance.imagen.name):
        instance.imagen.storage.delete(instance.imagen.name)

@receiver(pre_save, sender=ImagenServicio)
def reemplazo_archivo_imagen(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        anterior = ImagenServicio.objects.get(pk=instance.pk)
    except ImagenServicio.DoesNotExist:
        return
    if anterior.imagen and anterior.imagen != instance.imagen:
        if anterior.imagen.storage.exists(anterior.imagen.name):
            anterior.imagen.storage.delete(anterior.imagen.name)