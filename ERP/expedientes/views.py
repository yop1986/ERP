from itertools import product
from string import ascii_uppercase

from django.db.models import Count
from django.db.models.functions import Length
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy

from .models import Bodega, Estante, Nivel, Posicion, Caja, Folio
from .forms import Busqueda, GeneraEstructura
from usuarios.views_base import ListView_Login, DetailView_Login, CreateView_Login, UpdateView_Login, DeleteView_Login

# Create your views here.
class Inicio_Template(TemplateView):
    template_name = 'expedientes/index.html'
    extra_context = {
        'title': 'Expedientes',
    }


class Bodega_ListView(ListView_Login):
    model = Bodega
    permission_required = 'expedientes.view_bodega'
    paginate_by = 15
    ordering = ['-vigente', 'nombre']
    extra_context = {
        'title': _('Bodegas'),
        'opciones': {
            'etiqueta': _('Opciones'),
            'ver': _('Ver'),
            'editar': _('Editar'),
            'inhabilitar': _('Inhabilitar'),
            'habilitar': _('Habilitar'),
            'nuevo': _('Nuevo'),
        },
        'botones': {
            'buscar': _('Buscar'),
            'limpiar': _('Limpiar'),
        },
        'mensaje_vacio': _('No hay "Bodegas" registradas'),
    }

    def get_context_data(self, *args, **kwargs):
        busqueda = self.request.GET.get('valor')

        context = super().get_context_data(*args, **kwargs)
        context['url_lista'] = Bodega.list_url()
        if busqueda:
            context['object_list'] = Bodega.objects.filter(nombre__icontains=busqueda).order_by('nombre')
            context['form'] = Busqueda(self.request.GET)
        else:
            context['form'] = Busqueda()
        return context

class Bodega_DetailView(FormMixin, DetailView_Login):
    model = Bodega
    permission_required = 'expedientes.view_bodega'
    form_class = GeneraEstructura
    extra_context = {
        'title': _('Bodega'),
        'sub_titulo': {
            'genera': _('Genera Estructura'),
            'estructura': _('Estructura'),
        },
        'botones': {
            'generar': _('Generar'),
        }
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['opciones']={
            'etiqueta': _('Opciones'),
            'editar': _('Editar'),
            'accion': _('Inhabilitar') if self.object.vigente else _('Habilitar'),
            'accion_tag': 'danger' if self.object.vigente else 'success',
        }
        queryset = Estante.objects.filter(bodega=self.object).order_by(Length('codigo'), 'codigo')
        context['estructura']={
            'estantes': queryset,
            'no_columnas': queryset.count(),
            'tooltip': _('Nivel'),
            'niveles': Nivel.objects.filter(estante__bodega=self.object).order_by('numero', Length('estante__codigo'), 'estante__codigo')
        }
        return context

    def get_success_url(self, *args, **kwargs):
        return self.object.detail_url()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'Generar' in request.POST:
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else: 
                return self.form_invalid(form)
            #messages.warning(self.request, f'Ya esta registrado el origen "{od}" a este modelo');modelo');
    
    def form_valid(self, form, *args, **kwargs):
        e = form.cleaned_data['estantes']
        n = form.cleaned_data['niveles']
        p = form.cleaned_data['posiciones']
        c = form.cleaned_data['cajas']
        print(f">>>>>>>>>>>>>>>>>{e}, {n}, {p}, {c}")
        self._genera_estructura(e, n, p, c)

        return super().form_valid(form)

    def _genera_estructura(self, pEstantes, pNiveles, pPosiciones, pCajas):
        self._genera_estructura_estantes(pEstantes)
        self._genera_estructura_niveles(pNiveles)
        self._genera_estructura_posiciones(pPosiciones)
        self._genera_estructura_cajas(pCajas)
    
    def _genera_estructura_cajas(self, pCaja):
        inserts = []
        cajas = Caja.objects.filter(posicion__nivel__estante__bodega=self.object)
        for posicion in Posicion.objects.filter(nivel__estante__bodega=self.object, vigente=True):
            for i in range(1, pCaja+1):
                if not cajas.filter(numero=i, posicion=posicion):
                    inserts.append(Caja(numero=i, posicion=posicion))

        Caja.objects.bulk_create(inserts)

    def _genera_estructura_posiciones(self, pPosicion):
        inserts = []
        posiciones = Posicion.objects.filter(nivel__estante__bodega=self.object)
        for nivel in Nivel.objects.filter(estante__bodega=self.object, vigente=True):
            for i in range(1, pPosicion+1):
                if not posiciones.filter(numero=i, nivel=nivel):
                    inserts.append(Posicion(numero=i, nivel=nivel))

        Posicion.objects.bulk_create(inserts)

    def _genera_estructura_niveles(self, pNiveles):
        inserts = []
        niveles = Nivel.objects.filter(estante__bodega=self.object)
        for estante in Estante.objects.filter(bodega=self.object, vigente=True):
            for i in range(1, pNiveles+1):
                print(f"{estante}------{i}")
                if not niveles.filter(numero=i, estante=estante):
                    inserts.append(Nivel(numero=i, estante=estante))

        Nivel.objects.bulk_create(inserts)

    def _genera_estructura_estantes(self, pEstante):
        inserts = []
        estantes = Estante.objects.filter(bodega=self.object.id)

        for codigo in self._codigo_estante(pEstante):
            if not estantes.filter(codigo=codigo):
                inserts.append(Estante(codigo=codigo, bodega=self.object))

        Estante.objects.bulk_create(inserts)

    def _codigo_estante(self, numero=0):
        codigos = []
        for i in range(numero):
            c1 = i // 26
            c2 = i - c1*26
            codigos.append('{}{}'.format('' if i<26 else ascii_uppercase[c1-1],ascii_uppercase[c2]))
            i+=1
        return codigos

class Bodega_CreateView(CreateView_Login):
    permission_required = 'expedientes.add_bodega'
    model = Bodega
    fields = ['codigo', 'nombre', 'direccion']
    template_name = 'expedientes/form.html'
    extra_context = {
        'title': _('Nueva Bodega'),
        'botones': {
            'guardar': _('Guardar'),
            'cancelar': _('Cancelar'),
        },
        'list_url': reverse_lazy('expedientes:bodega_list'),
    }

class Bodega_UpdateView(UpdateView_Login):
    permission_required = 'expedientes.change_bodega'
    model = Bodega
    fields = ['codigo', 'nombre', 'direccion']
    template_name = 'expedientes/form.html'
    extra_context = {
        'title': _('Modificar Bodega'),
        'botones': {
            'guardar': _('Guardar'),
            'cancelar': _('Cancelar'),
        },
        'list_url': reverse_lazy('expedientes:bodega_list'),
    }

class Bodega_DeleteView(DeleteView_Login):
    permission_required = 'expedientes.change_bodega'
    model = Bodega
    template_name = 'expedientes/confirmation_form.html'
    extra_context = {
        'title': _('Cambiar Estado Bodega'),
        'list_url': reverse_lazy('expedientes:bodega_list'),
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['botones']={
            'guardar':_('Inhabilitar') if self.object.vigente else _('Habilitar'),
            'cancelar': _('Cancelar'),
            'tag': _('danger') if self.object.vigente else _('success'),
        }
        accion = context['botones']['guardar'].lower()
        context['mensajes']={
            'confirmacion': _(f'¿Quiere {accion} el elemento indicado?'),
        }
        return context

    def get_success_url(self, *args, **kwargs):
        return super().get_success_url(self.object.vigente)


class Estante_DetailView(DetailView_Login):
    model = Estante
    permission_required = 'expedientes.view_estante'
    extra_context = {
        'title': _('Estante'),
        'sub_titulo': {
            'estructura': _('Estructura'),
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        
        queryset = Nivel.objects.filter(estante=self.object).order_by('numero')
        context['estructura']={
            'niveles': queryset,
            'no_columnas': queryset.count(),
            'tooltip': _('Posición'),
            'posiciones': Posicion.objects.filter(nivel__estante=self.object).order_by('numero', 'nivel__numero')
        }
        return context


class Nivel_DetailView(DetailView_Login):
    model = Nivel
    permission_required = 'expedientes.view_nivel'
    extra_context = {
        'title': _('Nivel'),
        'sub_titulo': {
            'estructura': _('Estructura'),
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        
        queryset = Posicion.objects.filter(nivel=self.object).order_by('numero')
        context['estructura']={
            'posiciones': queryset,
            'no_columnas': queryset.count(),
            'tooltip': _('Caja'),
            'cajas': Caja.objects.filter(posicion__nivel=self.object).order_by('numero', 'posicion__numero')
        }
        return context


class Posicion_DetailView(DetailView_Login):
    model = Posicion
    permission_required = 'expedientes.view_posicion'
    extra_context = {
        'title': _('Posición'),
        'sub_titulo': {
            'estructura': _('Estructura'),
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        
        queryset = Caja.objects.filter(posicion=self.object).order_by('numero')
        context['estructura']={
            'cajas': queryset,
            'no_columnas': queryset.count(),
            'tooltip': _('Folio'),
            'folios': Folio.objects.filter(caja__posicion=self.object).order_by('credito__numero', 'numero')
        }
        return context


class Caja_DetailView(DetailView_Login):
    model = Caja
    permission_required = 'expedientes.view_caja'
    extra_context = {
        'title': _('Caja'),
        'sub_titulo': {
            'estructura': _('Estructura'),
        },
    }

class Caja_UpdateView(UpdateView_Login):
    pass

class Caja_DeleteView(DeleteView_Login):
    pass