from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    """
    Middleware que obliga a iniciar sesión para acceder a rutas específicas.
    En este caso, protege todo lo que empiece con /adminpanel/
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/adminpanel/') and not request.user.is_authenticated:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")
        return self.get_response(request)
