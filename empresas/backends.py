from django.core.mail.backends.smtp import EmailBackend as BaseSMTPBackend
from .utils import obtener_empresa_activa

class EmpresaSMTPBackend(BaseSMTPBackend):
    """
    Backend de correo que extrae los ajustes SMTP de la Empresa activa en la BD.
    Si no hay empresa activa, usará los valores por defecto declarados en settings.py.
    """

    def __init__(self, *args, **kwargs):
        # Intentamos obtener la empresa activa
        empresa = obtener_empresa_activa()

        if empresa:
            # Si encuentras campos no nulos en empresa, los asignas a kwargs
            if empresa.smtp_host:
                kwargs['host'] = empresa.smtp_host
            if empresa.smtp_port:
                kwargs['port'] = empresa.smtp_port
            if empresa.smtp_user:
                kwargs['username'] = empresa.smtp_user
            if empresa.smtp_password:
                kwargs['password'] = empresa.smtp_password
            # OJO: Django distingue entre use_tls y use_ssl. Asegúrate de no activar ambos a True.
            kwargs['use_tls'] = empresa.smtp_use_tls
            kwargs['use_ssl'] = empresa.smtp_use_ssl

        # Llamamos al constructor padre con los valores finales en kwargs
        super().__init__(*args, **kwargs)