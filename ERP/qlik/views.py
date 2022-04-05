from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin
from django.utils.translation import gettext as _

from .models import Stream, Modelo, TipoDato, OrigenDato, OrigenDatoModelo
from .forms import Busqueda, Stream_CreateForm, Modelo_CreateForm, OrigenDato_CreateForm, ModeloUsaDato_Form, ModeloGeneraDato_Form
from usuarios.views_base import ListView_Login, DetailView_Login, CreateView_Login, UpdateView_Login, DeleteView_Login


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
        return self.get_object().detail_url()

class Stream_CreateView(CreateView_Login):
    model = Stream
    permission_required = 'qlik.add_stream'
    form_class = Stream_CreateForm
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
    form_class = Stream_CreateForm
    extra_context = {
        'title': _('Modificar Stream'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

    def get_success_url(self):
        return self.object.detail_url()

class Stream_DeleteView(DeleteView_Login):
    pass



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
            'usa_datos': _('Usa datos'),
            'genera_datos': _('Genera datos'),
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
            tipodato = form.cleaned_data['tipodato']
            od = OrigenDato.objects.filter(nombre=nombre, tipodato=tipodato)
            if od.exists():
                messages.warning(self.request, f'Ya esta registrado el origen "{nombre}" en el modelo {od.modelo}');
            else:
                OrigenDato.objects.create(nombre=nombre, tipodato=tipodato, modelo=self.get_object()).save()         
        return super(Modelo_DetailView, self).form_valid(form)

    def get_success_url(self):
        return self.get_object().detail_url()
    
class Modelo_CreateView(CreateView_Login):
    model = Modelo
    permission_required = 'qlik.add_modelo'
    fields = ['nombre', 'descripcion', 'qlik_id', 'stream']
    template_name = 'qlik/form.html'
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
    fields = ['nombre', 'descripcion', 'qlik_id', 'stream']
    template_name = 'qlik/form.html'
    extra_context = {
        'title': _('Modificar Modelo'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

    def get_success_url(self):
        return self.object.detail_url()

class Modelo_DeleteView(DeleteView_Login):
    pass



class TipoDato_ListView(ListView_Login):
    model = TipoDato
    permission_required = 'qlik.view_tipodato'
    paginate_by = 15
    ordering = ['nombre']
    extra_context = {
        'title': _('Tipos de Datos'),
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
        'mensaje_vacio': _('No hay "Tipos de datos" registrados'),
    }

    def get_context_data(self, *args, **kwargs):
        busqueda = self.request.GET.get('valor')

        context = super().get_context_data(*args, **kwargs)
        context['url_lista'] = TipoDato.list_url()
        if busqueda:
            context['object_list'] = TipoDato.objects.filter(nombre__icontains=busqueda).order_by('nombre')
            context['form'] = Busqueda(self.request.GET)
        else:
            context['form'] = Busqueda()
        return context

class TipoDato_DetailView(DetailView_Login):
    model = TipoDato
    permission_required = 'qlik.view_tipodato'
    extra_context = {
        'title': _('Tipo de Dato'),
        'sub_titulo': {
            'origenes': _('Origen de Datos'),
        },
        'opciones': {
            'etiqueta': _('Opciones'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'eliminar': _('Eliminar'),
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super(TipoDato_DetailView, self).get_context_data(*args, **kwargs)
        context['origenes'] = self.object.get_origenes()
        return context

class TipoDato_CreateView(CreateView_Login):
    model = TipoDato
    permission_required = 'qlik.add_tipodato'
    template_name = 'qlik/form.html'
    fields = ['nombre', 'origenmodelo']
    extra_context = {
        'title': _('Nuevo Tipo de Dato'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

    def get_success_url(self):
        return TipoDato.list_url()

class TipoDato_UpdateView(UpdateView_Login):
    model = TipoDato
    permission_required = 'qlik.change_tipodato'
    template_name = 'qlik/form.html'
    fields = ['nombre', 'origenmodelo', 'vigente']
    extra_context = {
        'title': _('Modificar Tipo de Dato'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

    def get_success_url(self):
        return self.object.detail_url()

class TipoDato_DeleteView(DeleteView_Login):
    pass



class OrigenDato_ListView(ListView_Login):
    model = OrigenDato
    permission_required = 'qlik.view_origendato'
    paginate_by = 15
    ordering = ['nombre', 'tipodato__nombre']
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
    form_class = OrigenDato_CreateForm
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
    fields = ['nombre', 'tipodato']
    template_name = 'qlik/form.html'
    extra_context = {
        'title': _('Modificar Origen de Datos'),
        'botones': {
            'guardar': _('Guardar'),
        }
    }

    def get_success_url(self):
        return self.object.detail_url()

class OrigenDato_DeleteView(DeleteView_Login):
    pass


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
        return self.object.modelo.detail_url()


###
###
###
def ajax_origenes_asociados(request):
    tipo_dato_id = request.GET.get('tipo_origen_id')
    origenes = OrigenDato.objects.filter(tipodato=tipo_dato_id, vigente=True).order_by('nombre')
    return render(request, 'qlik/modelo_detail_origenes_dropdown.html', {'origenes': origenes})