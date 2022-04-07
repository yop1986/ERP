from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.translation import gettext as _


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