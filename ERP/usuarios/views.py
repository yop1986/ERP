from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as views_auth
from django.contrib.messages.views import SuccessMessageMixin
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
        if('expedientes' in settings.INSTALLED_APPS):
            apps['expedientes'] = {
                'image': 'images/expedientes.png',
                'nombre': 'Expedientes',
                'descripcion': 'Control de expedientes en bodega.',
                'url': reverse_lazy('expedientes:index'),
            }
        if('qlik' in settings.INSTALLED_APPS):
            apps['qlik'] = {
                'image': 'images/qlik.png',
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
    permission_required = 'usuarios.view_usuario'
    template_name = 'registration/perfil.html'
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
    permission_required = 'usuarios.change_usuario'
    template_name = 'registration/form.html'
    model = Usuario
    fields = ['first_name', 'last_name', 'email']
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
    template_name='registration/form.html'
    success_url = reverse_lazy('perfil')
    extra_context = {
        'title': _('Cambio de Contraseña'),
        'botones': {
            'guardar': _('Cambiar'),
        }
    }

class PasswordResetView(SuccessMessageMixin, views_auth.PasswordResetView):
    template_name = 'registration/form.html'
    extra_context = {
        'title': _('Recuperar Contraseña'),
        'botones': {
            'guardar': _('Recuperar'),
        }
    }
    subject_template_name = "registration/pass_reset_subject.txt"
    email_template_name = "registration/pass_reset_email.html"
    success_message = _('Se envio un correo con instrucciones, por favor revise.')
    success_url = reverse_lazy("usuarios:index")

class PasswordResetConfirmView(views_auth.PasswordResetConfirmView):
    pass

class PasswordResetDoneView(views_auth.PasswordResetDoneView):
    #template_name = 'registration/form.html'
    extra_context = {
        'title': _('Recuperar Contraseña'),
        'botones': {
            'guardar': _('Recuperar'),
        }
    }
    