from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.translation import gettext as _

from .models import Stream, Modelo, TipoDato, OrigenDato, OrigenDatoModelo

class Busqueda(forms.Form):
    valor = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valor'].label = False
        self.fields['valor'].widget.attrs.update({'class':'form-control'})


class Stream_CreateForm(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ['nombre', 'qlik_id']
        error_messages = {
            'qlik_id': {
                'invalid': _('Ingrese un ID válido')
            }
        }

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
    #    self.fields['nombre'].widget.attrs.update({'class':'form-control'})
    #    self.fields['qlik_id'].widget.attrs.update({'class':'form-control'})


class Modelo_CreateForm(forms.ModelForm):
    '''
        Stream_DetailView
        Formulario para agregar modelo al stream actual
    '''
    class Meta:
        model = Modelo
        fields = ['nombre', 'qlik_id']
        error_messages = {
            #'NON_FIELD_ERRORS': {
            #    'unique_together': _('%(nombre)s y %(qlik_id)s no son únicos.'),
            #},
            'qlik_id': {
                #'max_length': _("This writer's name is too long."),
                'invalid': _('Ingrese un ID válido')
            }
        }

class ModeloUsaDato_Form(forms.ModelForm):
    '''
        Modelo_DetailView
        Agrega el origen de datos que utiliza el modelo
    '''
    tipodato = forms.ModelChoiceField(queryset=TipoDato.objects.filter(vigente=True).order_by('nombre'))
    class Meta:
        model = OrigenDatoModelo
        fields = ['tipodato', 'origendato']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipodato'].label = _('Tipo de Dato')
        self.fields['origendato'].queryset = OrigenDato.objects.none()

        if 'tipodato' in self.data:
            try:
                tipodato_id = int(self.data.get('tipodato'))
                self.fields['origendato'].queryset = OrigenDato.objects.filter(tipodato_id=tipodato_id).order_by('nombre')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['origendato'].queryset = self.instance.tipodato.origendato_set.order_by('nombre')
    

class ModeloGeneraDato_Form(forms.ModelForm):
    '''
        Modelo_DetailView
        Permite definir origenes de datos que genera el modelo actual
    '''
    class Meta:
        model = OrigenDato
        fields = ['nombre', 'tipodato']
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': _('Nombre y tipo de dato no son únicos.'),
            },
        }

    def __init__(self, *args, **kwargs):
        super(ModeloGeneraDato_Form, self).__init__(*args, **kwargs)
        self.fields['tipodato'].queryset = TipoDato.objects.filter(vigente=True, origenmodelo=True).order_by('nombre')


class OrigenDato_CreateForm(forms.ModelForm):
    '''
        Form para Crear Origen de datos en el CreateView
    '''
    class Meta:
        model = OrigenDato
        fields = ['nombre', 'tipodato']
    
    def __init__(self, *args, **kwargs):
        super(OrigenDato_CreateForm, self).__init__(*args, **kwargs)
        self.fields['tipodato'].queryset = TipoDato.objects.filter(vigente=True, origenmodelo=False)