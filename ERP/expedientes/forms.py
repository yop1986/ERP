from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import gettext as _

from .models import Bodega
from usuarios.models import Usuario

class Busqueda(forms.Form):
    valor = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valor'].label = False
        self.fields['valor'].widget.attrs.update({'class':'form-control'})


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


class GeneraEtiquetas_Form(forms.Form):
    posicion = forms.IntegerField(min_value=1, max_value=26)

class CargaCreditos_Form(forms.Form):
    archivo = forms.FileField(label='Archivo')


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
    bodega_envio = forms.ModelChoiceField(queryset=Bodega.objects.all(),
        required=True, help_text=_('Bodega a donde se envían los expedientes'))
    comentario = forms.CharField(max_length=150, required=False)


class SalidaTomos_Form(forms.Form):
    codigo = forms.IntegerField(required=True, help_text=_('Código de colaborador'))
    nombre = forms.CharField(max_length=60, required=True, help_text=_('Nombre del colaborador'))
    extension = forms.CharField(max_length=6, required=False, help_text=_('Extensión del colaborador'))
    correo = forms.EmailField(max_length=120, required=True, help_text=_('Correo del colaborador'))
    gerencia = forms.CharField(max_length=60, required=True, help_text=_('Gerencia a la que pertenece'))
    comentario = forms.CharField(max_length=254, required=False)

class Bodega_From(forms.ModelForm):
    class Meta:
        model = Bodega
        fields= ['codigo', 'nombre', 'direccion', 'encargado']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['encargado'].queryset = Usuario.objects.filter(groups__name='Expedientes')

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()