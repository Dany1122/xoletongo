from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Empresa

@receiver(pre_save, sender=Empresa)
def asegurar_una_empresa_activa(sender, instance, **kwargs):
    if instance.activa:
        sender.objects.exclude(id=instance.id).update(activa=False)