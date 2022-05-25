from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils.translation import gettext as _

from .models import Stream, Modelo, TipoDato, OrigenDato, OrigenDatoModelo, Permiso

class Busqueda(forms.Form):
    valor = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['valor'].label = False
        self.fields['valor'].widget.attrs.update({'class':'form-control'})


class Stream_Form(forms.ModelForm):
    class Meta:
        model = Stream
        fields = ['nombre', 'qlik_id']
        error_messages = {
            'qlik_id': {
                'invalid': _('Ingrese un ID válido')
            }
        }


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


class Modelo_Form(forms.ModelForm):
    '''
        Creación de modelos
    '''
    class Meta:
        model = Modelo
        fields = ['nombre', 'descripcion', 'qlik_id', 'stream']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stream'].queryset = Stream.objects.all().order_by('nombre')


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
        super().__init__(*args, **kwargs)
        self.fields['tipodato'].queryset = TipoDato.objects.filter(vigente=True, origenmodelo=True).order_by('nombre')


class OrigenDato_Form(forms.ModelForm):
    '''
        Form para Crear Origen de datos en el CreateView
    '''
    class Meta:
        model = OrigenDato
        fields = ['nombre', 'tipodato']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipodato'].queryset = TipoDato.objects.filter(vigente=True, origenmodelo=False).order_by('nombre')


class AsignaPermiso_Form(forms.ModelForm):
    '''
        Permiso_CreateView
        Permite llevar el control de los permisos a los objetos
    '''
    objeto = forms.ModelChoiceField(queryset=TipoDato.objects.none())
    
    class Meta:
        model = Permiso
        fields = ['tobjeto', 'objeto', 'nombre', 'licencias', 'create', 'read', 'update', 'delete', 
        'export', 'publish', 'change_owner', 'export_data', 'access_offline', 'duplicate', 'approve'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['licencias'].queryset = self.fields['licencias'].queryset.order_by('nombre')
        
        if 'tobjeto' in self.data:
            try:
                self.fields['objeto'].queryset = globals()[self.data['tobjeto']].objects.all()
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            pass #self.fields['objeto'].queryset = self.instance.tobjeto.origendato_set.order_by('nombre')

    def save(self, commit=True):
        form_data = self.cleaned_data
        self.instance.obj_id = form_data['objeto'].id
        return super().save(commit)

class ModificaPermiso_Form(forms.ModelForm):
    '''
        Permiso_UpdateView
        Permite llevar el control de los permisos a los objetos
    '''
    class Meta:
        model = Permiso
        fields = ['nombre', 'licencias', 'create', 'read', 'update', 'delete', 
        'export', 'publish', 'change_owner', 'export_data', 'access_offline', 'duplicate', 'approve'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['licencias'].queryset = self.fields['licencias'].queryset.order_by('nombre')
        