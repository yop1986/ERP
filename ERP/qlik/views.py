from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin
from django.utils.translation import gettext as _

from .models import (Stream, Modelo, Repositorio, OrigenDato, OrigenDatoModelo, TipoLicencia, 
    Licencia, Permiso)
from .forms import (Busqueda, Stream_Form, Modelo_CreateForm, Modelo_Form, OrigenDato_Form, 
    ModeloUsaDato_Form, ModeloGeneraDato_Form, AsignaPermiso_Form, ModificaPermiso_Form)
from usuarios.views_base import (ListView_Login, DetailView_Login, CreateView_Login, UpdateView_Login, 
    DeleteView_Login)


class Inicio_Template(TemplateView):
    template_name = 'qlik/index.html'
    extra_context = {
        'title': 'Qlik Sense',
    }



class Stream_ListView(ListView_Login):
    model = Stream
    permission_required = 'qlik.view_stream'
    paginate_by = 15
    ordering = ['nombre']
    extra_context = {
        'title': _('Streams'),
        'opciones': {
            'etiqueta': _('Opciones'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
            'ir': _('Ir'),
            'nuevo': _('Nuevo'),
        },
        'botones': {
            'buscar': _('Buscar'),
            'limpiar': _('Limpiar'),
        },
        'mensaje_vacio': _('No hay "Streams" registrados'),
    }

    def get_context_data(self, *args, **kwargs):
        busqueda = self.request.GET.get('valor')

        context = super().get_context_data(*args, **kwargs)
        context['url_lista'] = Stream.list_url()
        if busqueda:
            context['object_list'] = Stream.objects.filter(nombre__icontains=busqueda).order_by('nombre')
            context['form'] = Busqueda(self.request.GET)
        else:
            context['form'] = Busqueda()
        return context

class Stream_DetailView(FormMixin, DetailView_Login):
    model = Stream
    permission_required = 'qlik.view_stream'
    form_class = Modelo_CreateForm
    extra_context = {
        'title': _('Stream'),
        'sub_titulo': {
            'modelos': _('Modelos'),
            'permisos': _('Permisos'),
        },
        'opciones': {
            'etiqueta': _('Opciones'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
            'ir': _('Ir'),
        },
        'botones': {
            'guardar': _('Guardar'),
        }
    }

    def get_context_data(self, *args, **kwargs):
        context = super(Stream_DetailView, self).get_context_data(*args,**kwargs)
        context['modelos'] = self.object.get_modelos().order_by('nombre')
        context['permisos'] = self.object.get_permisos()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, *args, **kwargs):
        nombre = form.cleaned_data['nombre']
        qlikid = form.cleaned_data['qlik_id']
        if Modelo.objects.filter(stream=self.get_object(), nombre=nombre).exists():
            messages.warning(self.request, f'Ya esta registrado el modelo "{nombre}" en el Stream.');
        else:    
            Modelo.objects.create(stream=self.get_object(), nombre=nombre, qlik_id=qlikid).save()
        return super(Stream_DetailView, self).form_valid(form)

    def get_success_url(self):
        return self.get_object().view_url()

class Stream_CreateView(CreateView_Login):
    model = Stream
    permission_required = 'qlik.add_stream'
    form_class = Stream_Form
    template_name = 'qlik/form.html'
    extra_context = {
        'title': _('Nuevo Stream'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

    def get_success_url(self):
        return Stream.list_url()

class Stream_UpdateView(UpdateView_Login):
    model = Stream
    permission_required = 'qlik.change_stream'
    template_name = 'qlik/form.html'
    form_class = Stream_Form
    extra_context = {
        'title': _('Modificar Stream'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

class Stream_DeleteView(DeleteView_Login):
    permission_required = 'qlik.delete_stream'
    template_name = 'qlik/confirmation_form.html'
    model = Stream
    extra_context = {
        'title': _('Eliminar stream'),
        'confirmacion': _('Esta seguro de eliminar el elemento'),
        'botones': {
            'eliminar': _('Eliminar'),
            'cancelar': _('Cancelar'),
        }
    }



class Modelo_ListView(ListView_Login):
    model = Modelo
    permission_required = 'qlik.view_modelo'
    paginate_by = 15
    ordering = ['nombre']
    extra_context = {
        'title': _('Modelos'),
        'opciones': {
            'etiqueta': _('Opciones'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
            'ir': _('Ir'),
            'nuevo': _('Nuevo'),
        },
        'botones': {
            'buscar': _('Buscar'),
            'limpiar': _('Limpiar'),
        },
        'mensaje_vacio': _('No hay "Modelos" registrados'),
    }

    def get_context_data(self, *args, **kwargs):
        busqueda = self.request.GET.get('valor')

        context = super().get_context_data(*args, **kwargs)
        context['url_lista'] = Modelo.list_url()
        if busqueda:
            context['object_list'] = Modelo.objects.filter(nombre__icontains=busqueda).order_by('nombre')
            context['form'] = Busqueda(self.request.GET)
        else:
            context['form'] = Busqueda()
        return context

class Modelo_DetailView(FormMixin, DetailView_Login):
    model = Modelo
    permission_required = 'qlik.view_modelo'
    form_class = ModeloUsaDato_Form
    extra_context = {
        'title': _('Modelo'),
        'sub_titulo': {
            'datos': _('Datos'),
            'usa_datos': _('Usa datos'),
            'genera_datos': _('Genera datos'),
            'permisos': _('Permisos'),
        },
        'opciones': {
            'etiqueta': _('Opciones'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
            'ir': _('Ir'),
        },
        'botones': {
            'usa': _('Usa'),
            'genera': _('Genera'),
        }
    }

    def get_context_data(self, *args, **kwargs):
        context = super(Modelo_DetailView, self).get_context_data(*args, **kwargs)
        context['origendatomodelo'] = self.get_object().get_origenes_usados()
        context['origendato'] = self.get_object().get_origenes_generados()
        context['permisos'] = self.get_object().get_permisos()
        post = self.request.POST if 'Usa' in self.request.POST else None
        context['form'] = ModeloUsaDato_Form(post)
        post = self.request.POST if 'Genera' in self.request.POST else None
        context['genera_form'] = ModeloGeneraDato_Form(post)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'Usa' in request.POST:
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form, formulario='Usa')
            else:
                return self.form_invalid(form)
        elif 'Genera' in request.POST:
            form = ModeloGeneraDato_Form(request.POST)
            if form.is_valid():
                return self.form_valid(form, formulario='Genera')
            else:
                return self.render_to_response(self.get_context_data(request=request, form=self.get_form(), genera_form=form))

    def form_valid(self, form, *args, **kwargs):
        if kwargs['formulario']=='Usa':
            od = form.cleaned_data['origendato']
            if OrigenDatoModelo.objects.filter(modelo=self.get_object(), origendato=od).exists():
                messages.warning(self.request, f'Ya esta registrado el origen "{od}" a este modelo');
            else:    
                OrigenDatoModelo.objects.create(modelo=self.get_object(), origendato=form.cleaned_data['origendato']).save()
        elif kwargs['formulario']=='Genera':
            nombre = form.cleaned_data['nombre']
            repositorio = form.cleaned_data['repositorio']
            od = OrigenDato.objects.filter(nombre=nombre, repositorio=repositorio)
            if od.exists():
                messages.warning(self.request, f'Ya esta registrado el origen "{nombre}" en el modelo {od.modelo}');
            else:
                OrigenDato.objects.create(nombre=nombre, repositorio=repositorio, modelo=self.get_object()).save()         
        return super(Modelo_DetailView, self).form_valid(form)

    def get_success_url(self):
        return self.get_object().view_url()
    
class Modelo_CreateView(CreateView_Login):
    model = Modelo
    permission_required = 'qlik.add_modelo'
    template_name = 'qlik/form.html'
    form_class = Modelo_Form
    extra_context = {
        'title': _('Nuevo Modelo'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

    def get_success_url(self):
        return Modelo.list_url()

class Modelo_UpdateView(UpdateView_Login):
    model = Modelo
    permission_required = 'qlik.change_modelo'
    template_name = 'qlik/form.html'
    form_class = Modelo_Form
    extra_context = {
        'title': _('Modificar Modelo'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

class Modelo_DeleteView(DeleteView_Login):
    permission_required = 'qlik.delete_modelo'
    template_name = 'qlik/confirmation_form.html'
    model = Modelo
    extra_context = {
        'title': _('Eliminar modelo'),
        'confirmacion': _('Esta seguro de eliminar el elemento'),
        'botones': {
            'eliminar': _('Eliminar'),
            'cancelar': _('Cancelar'),
        }
    }



class Repositorio_ListView(ListView_Login):
    model = Repositorio
    permission_required = 'qlik.view_repositorio'
    paginate_by = 15
    ordering = ['nombre']
    extra_context = {
        'title': _('Repositorio'),
        'opciones': {
            'etiqueta': _('Opciones'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
            'nuevo': _('Nuevo'),
        },
        'botones': {
            'buscar': _('Buscar'),
            'limpiar': _('Limpiar'),
        },
        'mensaje_vacio': _('No hay "Repositorios" registrados'),
    }

    def get_context_data(self, *args, **kwargs):
        busqueda = self.request.GET.get('valor')

        context = super().get_context_data(*args, **kwargs)
        context['url_lista'] = Repositorio.list_url()
        if busqueda:
            context['object_list'] = Repositorio.objects.filter(nombre__icontains=busqueda).order_by('nombre')
            context['form'] = Busqueda(self.request.GET)
        else:
            context['form'] = Busqueda()
        return context

class Repositorio_DetailView(DetailView_Login):
    model = Repositorio
    permission_required = 'qlik.view_repositorio'
    extra_context = {
        'title': _('Repositorio'),
        'sub_titulo': {
            'origenes': _('Origen de Datos'),
            'permisos': _('Permisos'),
        },
        'opciones': {
            'etiqueta': _('Opciones'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super(Repositorio_DetailView, self).get_context_data(*args, **kwargs)
        context['origenes'] = self.object.get_origenes()
        context['permisos'] = self.object.get_permisos()
        return context

class Repositorio_CreateView(CreateView_Login):
    model = Repositorio
    permission_required = 'qlik.add_repositorio'
    template_name = 'qlik/form.html'
    fields = ['nombre', 'origenmodelo']
    extra_context = {
        'title': _('Nuevo Repositorio'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

    def get_success_url(self):
        return Repositorio.list_url()

class Repositorio_UpdateView(UpdateView_Login):
    model = Repositorio
    permission_required = 'qlik.change_repositorio'
    template_name = 'qlik/form.html'
    fields = ['nombre', 'origenmodelo', 'vigente']
    extra_context = {
        'title': _('Modificar Repositorio'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

class Repositorio_DeleteView(DeleteView_Login):
    permission_required = 'qlik.delete_repositorio'
    template_name = 'qlik/confirmation_form.html'
    model = Repositorio
    extra_context = {
        'title': _('Eliminar Repositorio'),
        'confirmacion': _('Esta seguro de eliminar el elemento'),
        'botones': {
            'eliminar': _('Eliminar'),
            'cancelar': _('Cancelar'),
        }
    }



class OrigenDato_ListView(ListView_Login):
    model = OrigenDato
    permission_required = 'qlik.view_origendato'
    paginate_by = 15
    ordering = ['nombre', 'repositorio__nombre']
    extra_context = {
        'title': _('Origenes de Datos'),
        'opciones': {
            'etiqueta': _('Opciones'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
            'nuevo': _('Nuevo'),
        },
        'botones': {
            'buscar': _('Buscar'),
            'limpiar': _('Limpiar'),
        },
        'mensaje_vacio': _('No hay "Origenes de datos" registrados'),
    }

    def get_context_data(self, *args, **kwargs):
        busqueda = self.request.GET.get('valor')

        context = super().get_context_data(*args, **kwargs)
        context['url_lista'] = OrigenDato.list_url()
        if busqueda:
            context['object_list'] = OrigenDato.objects.filter(nombre__icontains=busqueda).order_by('nombre')
            context['form'] = Busqueda(self.request.GET)
        else:
            context['form'] = Busqueda()
        return context

class OrigenDato_DetailView(DetailView_Login):
    model = OrigenDato
    permission_required = 'qlik.view_origendato'
    extra_context = {
        'title': _('Origen de Datos'),
        'sub_titulo': {
            'origendatomodelo': _('Usado por Modelos'),
        },
        'opciones': {
            'etiqueta': _('Opciones'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
            'ir': _('Ir'),
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['origendatomodelo'] = self.get_object().get_usadoxmodelo()
        return context

class OrigenDato_CreateView(CreateView_Login):
    model = OrigenDato
    permission_required = 'qlik.add_origendato'
    template_name = 'qlik/form.html'
    form_class = OrigenDato_Form
    extra_context = {
        'title': _('Nuevo Origen de Datos'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

    def get_success_url(self):
        return OrigenDato.list_url()

class OrigenDato_UpdateView(UpdateView_Login):
    model = OrigenDato
    permission_required = 'qlik.change_origendato'
    template_name = 'qlik/form.html'
    form_class = OrigenDato_Form
    extra_context = {
        'title': _('Modificar Origen de Datos'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

class OrigenDato_DeleteView(DeleteView_Login):
    permission_required = 'qlik.delete_origendato'
    template_name = 'qlik/confirmation_form.html'
    model = OrigenDato
    extra_context = {
        'title': _('Eliminar el origen de dato'),
        'confirmacion': _('Esta seguro de eliminar el elemento'),
        'botones': {
            'eliminar': _('Eliminar'),
            'cancelar': _('Cancelar'),
        }
    }

    def get_success_url(self, *args, **kwargs):
        if 'modelo' in self.kwargs:
            return Modelo.objects.get(id=self.kwargs['modelo']).view_url()
        else:
            return self.object.list_url()

class OrigenDatoModelo_DeleteView(DeleteView_Login):
    model = OrigenDatoModelo
    permission_required = 'qlik.delete_origendatomodelo'
    extra_context = {
        'title': _('Eliminar elemento'),
        'botones': {
            'confirmar': _('Confirmar'),
            'regresar': _('Regresar'),
        }
    }

    def get_success_url(self):
        return self.object.modelo.view_url()



class TipoLicencia_ListView(ListView_Login):
    permission_required = 'qlik.view_tipolicencia'
    model = TipoLicencia
    paginate_by = 15
    ordering = ['descripcion']
    extra_context = {
        'title': _('Tipos de Licencias'),
        'opciones': {
            'etiqueta': _('Opciones'),
            'nuevo': _('Nuevo Tipo'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
            'disponibles': _('Disponibles'),
        },
        'botones': {
            'buscar': _('Buscar'),
            'limpiar': _('Limpiar'),
        },
        'mensaje_vacio': _('No hay tipos de licencias registradas')
    }

    def get_context_data(self, *args, **kwargs):
        busqueda = self.request.GET.get('valor')

        context = super().get_context_data(*args, **kwargs)
        context['url_lista'] = TipoLicencia.list_url()
        if busqueda:
            context['object_list'] = TipoLicencia.objects.filter(descripcion__icontains=busqueda).order_by('descripcion')
            context['form'] = Busqueda(self.request.GET)
        else:
            context['form'] = Busqueda()
        return context

class TipoLicencia_DetailView(DetailView_Login):
    permission_required = 'qlik.view_tipolicencia'
    template_name = 'qlik/tipolicencia_detail.html'
    model = TipoLicencia
    extra_context = {
        'title': _('Tipo de Licencia'),
        'sub_titulo': {
            'licencias': _('Licencias'),
        },
        'opciones': {
            'etiqueta': _('Opciones'),
            'disponibles': _('Disponibles'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
        }
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['licencias'] = Licencia.objects.filter(tlicencia=self.object)
        return context

class TipoLicencia_CreateView(CreateView_Login):
    permission_required = 'qlik.add_tipolicencia'
    template_name = 'qlik/form.html'
    model = TipoLicencia
    fields = ['descripcion', 'cantidad']
    extra_context = {
        'title': _('Nuevo Tipo de Licencia'),
        'botones': {
            'guardar': _('Guardar'),
        },
    }

class TipoLicencia_UpdateView(UpdateView_Login):
    permission_required = 'qlik.change_tipolicencia'
    template_name = 'qlik/form.html'
    model = TipoLicencia
    fields = ['descripcion', 'cantidad']
    extra_context = {
        'title': _('Modificar Tipo de Licencia'),
        'botones': {
            'guardar': _('Modificar'),
        },
    }

class TipoLicencia_DeleteView(DeleteView_Login):
    permission_required = 'qlik.delete_tipolicencia'
    template_name = 'qlik/confirmation_form.html'
    model = TipoLicencia
    extra_context = {
        'title': _('Eliminar tipo de licencia'),
        'confirmacion': _('Esta seguro de eliminar el elemento'),
        'botones': {
            'eliminar': _('Eliminar'),
            'cancelar': _('Cancelar'),
        }
    }



class Licencia_ListView(ListView_Login):
    permission_required = 'qlik.view_licencia'
    model = Licencia
    paginate_by = 15
    ordering = ['nombre']
    extra_context = {
        'title': _('Licencias'),
        'opciones': {
            'etiqueta': _('Opciones'),
            'nuevo': _('Asignar'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
        },
        'botones': {
            'buscar': _('Buscar'),
            'limpiar': _('Limpiar'),
        },
        'mensaje_vacio': _('No hay licencias asignadas')
    }

    def get_context_data(self, *args, **kwargs):
        busqueda = self.request.GET.get('valor')

        context = super().get_context_data(*args, **kwargs)
        context['url_lista'] = Licencia.list_url()
        if busqueda:
            context['object_list'] = Licencia.objects.filter(Q(nombre__icontains=busqueda) | 
                Q(gerencia__icontains=busqueda) | Q(codigo__icontains=busqueda)).order_by('nombre')
            context['form'] = Busqueda(self.request.GET)
        else:
            context['form'] = Busqueda()
        return context

class Licencia_DetailView(DetailView_Login):
    permission_required = 'qlik.view_licencia'
    model = Licencia
    extra_context = {
        'title': _('Licencia'),
        'sub_titulo': {
            'permisos': _('Permisos'),
        },
        'opciones': {
            'etiqueta': _('Opciones'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
        }
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['permisos'] = Permiso.objects.filter(licencias=self.object)
        return context

class Licencia_CreateView(CreateView_Login):
    permission_required = 'qlik.add_licencia'
    template_name = 'qlik/form.html'
    model = Licencia
    fields = ['codigo', 'nombre', 'tusuario', 'gerencia', 'pais', 'tlicencia']
    extra_context = {
        'title': _('Asignación de Licencia'),
        'botones': {
            'guardar': _('Guardar'),
        },
    }

class Licencia_UpdateView(UpdateView_Login):
    permission_required = 'qlik.change_licencia'
    template_name = 'qlik/form.html'
    model = Licencia
    fields = ['codigo', 'nombre', 'tusuario', 'gerencia', 'pais', 'tlicencia']
    extra_context = {
        'title': _('Actualización de Licencia'),
        'botones': {
            'guardar': _('Modificar'),
        },
    }

class Licencia_DeleteView(DeleteView_Login):
    permission_required = 'qlik.delete_licencia'
    template_name = 'qlik/confirmation_form.html'
    model = Licencia
    extra_context = {
        'title': _('Desasignar licencia'),
        'confirmacion': _('Esta seguro de desasginar la licencia'),
        'botones': {
            'eliminar': _('Desasignar'),
            'cancelar': _('Cancelar'),
        }
    }



class Permiso_ListView(ListView_Login):
    permission_required = 'qlik.view_permiso'
    model = Permiso
    paginate_by = 15
    ordering = ['licencias__nombre', 'tobjeto']
    extra_context = {
        'title': _('Permisos'),
        'opciones': {
            'etiqueta': _('Opciones'),
            'nuevo': _('Asignar'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
        },
        'botones': {
            'buscar': _('Buscar'),
            'limpiar': _('Limpiar'),
        },
        'mensaje_vacio': _('No hay permisos asignadas')
    }

    def get_context_data(self, *args, **kwargs):
        busqueda = self.request.GET.get('valor')

        context = super().get_context_data(*args, **kwargs)
        context['url_lista'] = Permiso.list_url()
        if busqueda:
            context['object_list'] = Permiso.objects.filter(Q(licencia__nombre__icontains=busqueda) | 
                Q(tobjeto__icontains=busqueda)).order_by('licencia__nombre')
            context['form'] = Busqueda(self.request.GET)
        else:
            context['form'] = Busqueda()
        return context

class Permiso_DetailView(DetailView_Login):
    permission_required = 'qlik.view_permiso'
    model = Permiso
    extra_context = {
        'title': _('Permiso'),
        'etiquetas': {
            'permisos': _('Permisos'),
        },
        'opciones': {
            'etiqueta': _('Opciones'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
        }
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        #context['licencias'] = Permiso.objects.filter(licencia=self.object)
        return context

class Permiso_CreateView(CreateView_Login):
    permission_required = 'qlik.add_permiso'
    template_name = 'qlik/permiso_createform.html'
    form_class = AsignaPermiso_Form
    model = Permiso
    extra_context = {
        'title': _('Asignación de Permisos'),
        'botones': {
            'guardar': _('Asignar'),
        },
    }

class Permiso_UpdateView(UpdateView_Login):
    permission_required = 'qlik.change_permiso'
    template_name = 'qlik/permiso_updateform.html'
    model = Permiso
    form_class = ModificaPermiso_Form
    extra_context = {
        'title': _('Actualización de Permisos'),
        'botones': {
            'guardar': _('Modificar'),
        },
    }

class Permiso_DeleteView(DeleteView_Login):
    permission_required = 'qlik.delete_permiso'
    template_name = 'qlik/confirmation_form.html'
    model = Permiso
    extra_context = {
        'title': _('Remover acceso'),
        'botones': {
            'eliminar': _('Desasignar'),
            'cancelar': _('Cancelar'),
        }
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['confirmacion'] = _('Esta seguro de remover el acceso de ') + self.object.objeto.nombre + _(' al usuario ')
        return context



###
###
###
def ajax_origenes_asociados(request):
    '''
        Modelo_DetailView
        Origenes asociados
    '''
    tipo_dato_id = request.GET.get('repositorio_id')
    origenes = OrigenDato.objects.filter(repositorio=tipo_dato_id, vigente=True).order_by('nombre')
    return render(request, 'qlik/modelo_detail_origenes_dropdown.html', {'origenes': origenes})

def ajax_permisos_objetos(request):
    '''
        Permiso_CreateView
        Busca objetos de forma dinmaica con base en el tipo de objeto seleccionado
    '''
    tipo_objeto = request.GET.get('tipo_objeto')
    objetos = globals()[tipo_objeto].objects.all().order_by('nombre')
    return render(request, 'qlik/permiso_form_objetos.html', {'objetos': objetos})