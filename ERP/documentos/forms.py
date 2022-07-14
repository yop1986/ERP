from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from .models import Bodega, SolicitudFHA, Motivo, Solicitante
from usuarios.models import Usuario
     

class Busqueda(forms.Form):
    valor = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valor'].label = False
        self.fields['valor'].widget.attrs.update({'class':'form-control'})

class CargaCreditos_Form(forms.Form):
    archivo = forms.FileField(label='Archivo')

##########################################################################
# Expedientes
##########################################################################
class GeneraEstructura(forms.Form):
    '''
        Bodega Detail
        Permite generar la estructura (estantes, niveles y posiciones) de forma
        masiva para toda la bodega.
    '''
    estantes = forms.IntegerField(required=True, min_value=1)
    niveles = forms.IntegerField(required=True, min_value=1)
    posiciones = forms.IntegerField(required=True, min_value=1)
    cajas = forms.IntegerField(required=True, min_value=1)

class Bodega_From(forms.ModelForm):
    class Meta:
        model = Bodega
        fields= ['codigo', 'nombre', 'direccion', 'encargado', 'personal', 
        'correo_egreso', 'correo_traslado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        usuarios = Usuario.objects.filter(is_active=True, groups__name__istartswith='documentos').distinct()
        self.fields['encargado'].queryset = usuarios
        self.fields['personal'].queryset = usuarios

class IngresoTomo_Form(forms.Form):
    '''
        Permite el ingreso de tomos al archivo de forma individual asignando a
        una caja
    '''
    tomo = forms.CharField(required=True, help_text=_('Credito-Tomo'))
    caja = forms.CharField(required=True, help_text=_('Bodega-Estante-Nivel-Posición-Caja'))
    comentario = forms.CharField(max_length=254, required=False)

    def clean_tomo(self):
        data = self.cleaned_data['tomo'].replace(' ', '').split('-')
        if len(data)!=2 or not is_integer(data[1]):
            raise ValidationError(_('Formato de tomo incorrecto'))
        return data

    def clean_caja(self):
        data = self.cleaned_data['caja'].replace(' ', '').split('-')
        if len(data)!=5 or not (is_integer(data[2]) and is_integer(data[3]) and is_integer(data[4])):
            raise ValidationError(_('Formato de caja incorrecto'))
        return data

class EgresoTomo_Form(forms.Form):
    tomo = forms.CharField(required=True)

class TrasladoTomos_Form(forms.Form):
    bodega_envio = forms.ModelChoiceField(queryset=Bodega.objects.filter(vigente=True),
        required=True, help_text=_('Bodega a donde se envían los expedientes'))
    comentario = forms.CharField(max_length=150, required=False)

class SalidaTomos_Form(forms.Form):
    motivo = forms.ModelChoiceField(queryset=Motivo.objects.filter(vigente=True, area='EXP'), 
        required=True, help_text=_('Motivo de extracción'))
    solicitante = forms.ModelChoiceField(queryset=Solicitante.objects.filter(vigente=True, area='EXP'),
        required=True, help_text=_('Usuario que solicita documentos'))
#    codigo = forms.IntegerField(required=True, help_text=_('Código de colaborador'))
#    nombre = forms.CharField(max_length=60, required=True, 
#        help_text=_('Nombre del colaborador'))
#    extension = forms.CharField(max_length=6, required=False, 
#        help_text=_('Extensión del colaborador'))
#    correo = forms.EmailField(max_length=120, required=True, 
#        help_text=_('Correo del colaborador'))
#    gerencia = forms.CharField(max_length=60, required=True, 
#        help_text=_('Gerencia a la que pertenece'))
    comentario = forms.CharField(max_length=254, required=False)

##########################################################################
# Documentos FHA
##########################################################################
class SolicitudFHA_CreateForm(forms.ModelForm):
    '''
        SolicitudFHA_CreateView
        Creación de nuevas solicitudes
    '''
    class Meta:
        model = SolicitudFHA
        fields = ['solicitante', 'motivo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['solicitante'].queryset = self.fields['solicitante'].queryset.filter(vigente=True, area='FHA').order_by('nombre')
        self.fields['motivo'].queryset = self.fields['motivo'].queryset.filter(vigente=True, area='FHA').order_by('nombre')

class ExtraeBoveda_Form(forms.ModelForm):
    '''
        ExtraeBoveda_Form
        Formulario para registrar salida de bóveda
    '''
    class Meta:
        model = SolicitudFHA
        fields = ['poliza_egreso']

##########################################################################
# Funciones adicionales
##########################################################################
def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()