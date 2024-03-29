from django.conf import settings
from django.contrib.auth import views as views_auth
from django.db.models import Q
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.urls import reverse_lazy

from .models import Usuario
from .views_base import DetailView_Login, UpdateView_Login

# Create your views here.
class Inicio_Template(TemplateView):
    template_name = 'registration/index.html'
    extra_context = {
        'title': _('Modulos del ERP'),
        'ir': _('Ir...'),
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['aplicaciones'] = self.get_aplicaciones_instaladas()
        return context

    def get_aplicaciones_instaladas(self):
        apps = {}
        if('clientes' in settings.INSTALLED_APPS and (
                self.request.user.is_superuser or 
                self.request.user.groups.filter(name__istartswith='clientes'))
            ):
            apps['clientes'] = {
                'image': 'images/menu_clientes.png',
                'nombre': 'Clientes',
                'descripcion': 'Seguimiento de clientes.',
                'url': reverse_lazy('clientes:index'),
            }
        if('documentos' in settings.INSTALLED_APPS and (
                self.request.user.is_superuser or 
                self.request.user.groups.filter(name__istartswith='documentos'))
            ):
            apps['documentos'] = {
                'image': 'images/menu_documentos.png',
                'nombre': 'Documentos',
                'descripcion': 'Control de documentos en bodega.',
                'url': reverse_lazy('documentos:index'),
            }
        if('qlik' in settings.INSTALLED_APPS and (
                self.request.user.is_superuser or 
                self.request.user.groups.filter(name__istartswith='qlik'))
            ):
            apps['qlik'] = {
                'image': 'images/menu_qlik.png',
                'nombre': 'Qlik Sense',
                'descripcion': 'Herramienta de control para manejo de las estructuras asociadas a los modelos desarrollados en Qlik Sense.',
                'url': reverse_lazy('qlik:index'),
            }
        if('eventos' in settings.INSTALLED_APPS):
            apps['eventos'] = {
                'image': 'images/eventos.png',
                'nombre': 'Eventos',
                'descripcion': 'Capacitacion Django CODEMY.COM (https://www.youtube.com/watch?v=HHx3tTQWUx0&list=PLCC34OHNcOtqW9BJmgQPPzUpJ8hl49AGy).',
                'url': reverse_lazy('eventos:index'),
            }
        return apps


class Login(views_auth.LoginView):
    extra_context = {
        'title': _('Ingresar'),
        'botones': {
            'ingresar': _('Ingresar'),
            'salir': _('Salir'),
        },
        'mensajes': {
            'logueado': _('Usuario ya logueado.'),
        }
    }


class Perfil_Login(DetailView_Login):
    template_name = 'registration/perfil.html'
    permission_required = 'usuarios.view_usuario'
    extra_context = {
        'title': _('Perfil'),
        'etiquetas': {
            'nombre_completo': _('Nombre completo'),
            'grupos': _('Grupos'),
            'superusuario': _('Super Usuario'),
        },
    }

    def get_object(self):
        return Usuario.objects.get(pk=self.request.user.id)


class Perfil_Update(UpdateView_Login):
    template_name = 'registration/form.html'
    model = Usuario
    fields = ['first_name', 'last_name', 'email']
    permission_required = 'usuarios.change_usuario'
    extra_context = {
        'title': _('Actualizar Perfil'),
        'botones': {
            'guardar': _('Guardar'),
        },
    }

    def get_object(self):
        return Usuario.objects.get(pk=self.request.user.id)

    def get_success_url(self):
        return self.object.get_absolute_url()

class PasswordChangeView(views_auth.PasswordChangeView):
    template_name='registration/change_password.html'
    success_url = reverse_lazy('perfil')
    extra_context = {
        'title': _('Cambio de Contraseña'),
        'botones': {
            'guardar': _('Cambiar'),
        }
    }