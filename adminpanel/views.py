from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from usuarios.models import CustomUser
from reservaciones.models import Reservacion
from empresas.models import Empresa
from django.shortcuts import get_object_or_404, redirect
from adminpanel.forms import CustomUserForm


def dashboard(request):
    empresa = Empresa.objects.filter(activa=True).first()
    total_usuarios = CustomUser.objects.count()
    total_reservaciones = Reservacion.objects.count()
    return render(request, 'dashboard.html', {
        'empresa': empresa,
        'total_usuarios': total_usuarios,
        'total_reservaciones': total_reservaciones,
    })

def lista_usuarios(request):
    usuarios = CustomUser.objects.all().order_by('rol')
    context = {'usuarios': usuarios}
    return render(request, 'lista_usuarios.html', context)

def editar_usuario(request, id):
    usuario = get_object_or_404(CustomUser, id=id)
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('admin_usuarios')
    else:
        form = CustomUserForm(instance=usuario)
    return render(request, 'editar_usuario.html', {'form': form})

def eliminar_usuario(request, id):
    usuario = get_object_or_404(CustomUser, id=id)
    usuario.delete()
    return redirect('/adminpanel/usuarios/?eliminado=1')