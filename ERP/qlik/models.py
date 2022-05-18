import uuid

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib import messages

# Create your models here.
QLIK_PROXY = 'https://vmqlikviewger.bdr/'


class Stream(models.Model):
    ''' 
        Stream 
        Creado dentro de la herramienta Qlik Sense 
    '''
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre  = models.CharField(verbose_name=_('Nombre'), max_length=90, unique=True)
    qlik_id = models.UUIDField(verbose_name=_('Id Stream'), max_length=60, unique=True)
    
    def __str__(self):
        return self.nombre

    def get_modelos(self):
        '''Modelos asociados al Stream'''
        return Modelo.objects.filter(stream=self)

    def get_permisos(self):
        return Permiso.objects.filter(tobjeto='Stream', obj_id=self.id).prefetch_related('licencia')

    def list_url(self=None):
        return reverse('qlik:stream_list')

    def view_url(self):
        return reverse('qlik:stream_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('qlik:stream_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('qlik:stream_delete', kwargs={'pk': self.id})

    def external_url(self):
        return f'{QLIK_PROXY}hub/stream/{self.qlik_id}'

class Modelo(models.Model):
    ''' 
        Modelo de datos 
        Registrado en Qlik Sense
    '''
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre  = models.CharField(verbose_name=_('Nombre'), max_length=90)
    descripcion = models.CharField(verbose_name=_('Descripción'), max_length=210, blank=True)
    qlik_id = models.UUIDField(verbose_name=_('Id Modelo'), max_length=60, unique=True)
    stream  = models.ForeignKey(Stream, verbose_name=_('Stream'), on_delete=models.RESTRICT, related_name='modelo_stream')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'stream'], name='unq_nombre_stream'),
        ]

    def __str__(self):
        return self.nombre

    def get_resumen(self, max_length=60):
        return f'{self.descripcion[:max_length]}...'

    def get_origenes_usados(self):
        '''Origenes de datos que utiliza el modelo'''
        return OrigenDatoModelo.objects.filter(modelo=self).order_by('origendato__nombre')

    def get_origenes_generados(self):
        return OrigenDato.objects.filter(modelo=self).order_by('nombre')

    def get_permisos(self):
        return Permiso.objects.filter(tobjeto='Modelo', obj_id=self.id).prefetch_related('licencia')

    def list_url(self=None):
        return reverse('qlik:modelo_list')

    def view_url(self):
        return reverse('qlik:modelo_view', kwargs={'pk': self.id})
    
    def update_url(self):
        return reverse('qlik:modelo_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('qlik:modelo_delete', kwargs={'pk': self.id})

    def external_url(self):
        return f'{QLIK_PROXY}sense/app/{self.qlik_id}'

class TipoDato(models.Model):
    ''' 
        Tipo de dato
        También se puede utilizar para definir el origen de los datos y así filtrarlos 
    '''
    nombre  = models.CharField(verbose_name=_('Nombre'), max_length=90, unique=True)
    origenmodelo = models.BooleanField(verbose_name=_('Originado de modelo'), default=False)
    vigente = models.BooleanField(verbose_name=_('Estado'), default=True)
    
    def __str__(self):
        return self.nombre

    def get_si_origen_modelo(self):
        return _('Si') if self.origenmodelo else _('No')

    def get_estado(self):
        return _('Vigente') if self.vigente else _('No Vigente')

    def get_origenes(self):
        '''Origenes asociados al Stream'''
        return OrigenDato.objects.filter(tipodato=self, vigente=True)

    def get_permisos(self):
        return Permiso.objects.filter(tobjeto='TipoDato', obj_id=self.id).prefetch_related('licencia')

    def list_url(self=None):
        return reverse('qlik:tipodato_list')

    def view_url(self):
        return reverse('qlik:tipodato_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('qlik:tipodato_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('qlik:tipodato_delete', kwargs={'pk': self.id})

class OrigenDato(models.Model):
    '''
        Origen de los datos
        Define todos los datos que pueden ser consumidos por los modelos desde Qlik Sense
        Así como los modelos que dan origen a determinado set de datos (si fuera el caso)
    '''
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre  = models.CharField(verbose_name=_('Nombre'), max_length=90)
    vigente = models.BooleanField(verbose_name=_('Estado'), default=True)
    tipodato = models.ForeignKey(TipoDato, verbose_name=_('Tipo de dato'), on_delete=models.RESTRICT, related_name='origendato_tipodato')
    modelo  = models.ForeignKey(Modelo, verbose_name=_('Modelo'), on_delete=models.SET_NULL, blank=True, null=True, related_name='origendato_modelo')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'tipodato'], name='unq_nombre_tipodato'),
        ]

    def __str__(self):
        return self.nombre

    def get_estado(self):
        return _('Vigente') if self.vigente else _('No Vigente')

    def get_usadoxmodelo(self):
        return OrigenDatoModelo.objects.filter(origendato=self).order_by('modelo__nombre')

    def list_url(self=None):
        return reverse('qlik:origendato_list')

    def view_url(self):
        return reverse('qlik:origendato_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('qlik:origendato_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('qlik:origendato_delete', kwargs={'pk': self.id})

class OrigenDatoModelo(models.Model):
    '''
        OrigenDatoModelo
        Esta asociacion permite establecer que datos utiliza un modelo
    '''
    modelo  = models.ForeignKey(Modelo, verbose_name=_('Modelo'), on_delete=models.CASCADE, related_name='modelo_origendato')
    origendato = models.ForeignKey(OrigenDato, verbose_name=_('Origen de Dato'), on_delete=models.CASCADE, related_name='origendato_modelo')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['modelo', 'origendato'], name='unq_modelo_origendato'),
        ]

    def __str__(self):
        return f'{self.modelo} ({self.origendato})'

    def delete_url(self):
        return reverse('qlik:origendatomodelo_delete', kwargs={'pk': self.id})


class TipoLicencia(models.Model):
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(_('Descripción'), max_length = 15)
    cantidad    = models.PositiveSmallIntegerField(_('Cantidad'))

    def __str__(self):
        return self.descripcion

    @property
    def disponibles(self):
        return self.cantidad - Licencia.objects.filter(tlicencia = self.id).count()

    def list_url(self=None):
        return reverse('qlik:tipolicencia_list')

    def view_url(self):
        return reverse('qlik:tipolicencia_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('qlik:tipolicencia_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('qlik:tipolicencia_delete', kwargs={'pk': self.id})

class Licencia(models.Model):
    ''' 
        Licencia: 
        Usuarios con licencia asignada
    '''
    TIPO_USUARIO = [
        ('BDR', _('gfbanrural/usr')),
        ('OUT', _('gfbanrural/out')),
    ]
    
    # get_tusuario_display, get_tlicencia_display
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo      = models.PositiveIntegerField(_('Código'), unique=True)
    tusuario    = models.CharField(_('Tipo de Usuario'), max_length=3, choices=TIPO_USUARIO, default='BDR')
    nombre      = models.CharField(_('Nombre'), max_length=90)
    gerencia    = models.CharField(_('Gerencia'), max_length=90)
    pais        = models.CharField(_('País'), max_length=30)
    tlicencia   = models.ForeignKey(TipoLicencia,verbose_name=_('Tipo licencia'), on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.nombre} ({self.codigo})'

    @property
    def usuario_ad(self):
            return self.get_tusuario_display() + f'{self.codigo:06d}'

    def list_url(self=None):
        return reverse('qlik:licencia_list')

    def view_url(self):
        return reverse('qlik:licencia_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('qlik:licencia_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('qlik:licencia_delete', kwargs={'pk': self.id})

class Permiso(models.Model):
    '''
        Permiso:
        Establece los permisos para diferentes objetos
    '''
    MODELO_ASOCIADO = [
        ('Stream', 'Stream'),
        ('Modelo', _('Modelo')),
        ('TipoDato', _('Conexión')),
    ]

    # get_tobjeto_display
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    obj_id      = models.UUIDField(_('Object ID'))
    tobjeto     = models.CharField(_('Tipo de Objeto'), max_length=21, choices=MODELO_ASOCIADO)
    licencia    = models.ForeignKey(Licencia, verbose_name=_('Licencia'), on_delete=models.CASCADE, related_name='licencia_permiso')

    @property
    def objeto(self):
        return globals()[self.tobjeto].objects.get(id=self.obj_id)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['licencia', 'tobjeto', 'obj_id'], name='unq_licencia_objeto'),
        ]


    def __str__(self):
        return f'{self.licencia}'
        #return globals()[self.tobjeto].objects.get(id=self.obj_id).nombre

    def list_url(self=None):
        return reverse('qlik:permiso_list')

    def delete_url(self):
        return reverse('qlik:permiso_delete', kwargs={'pk': self.id})