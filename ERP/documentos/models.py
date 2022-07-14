import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from simple_history.models import HistoricalRecords

# Create your models here.
class Cliente(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.PositiveIntegerField(db_index=True, unique=True)
    nombre = models.CharField(max_length=210)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Moneda(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(max_length=21, unique=True)
    simbolo = models.CharField(max_length=1, unique=True, blank=True, null=True)
    
    def __str__(self):
        return f"{self.descripcion} ({self.simbolo})"

    
class Producto(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(max_length=21, unique=True)

    def __str__(self):
        return self.descripcion

    
class Oficina(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.PositiveIntegerField(db_index=True, unique=True)
    descripcion = models.CharField(max_length=90)

    def __str__(self):
        return f"{str(self.numero).zfill(4)} - {self.descripcion}"

    
class Credito(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero  = models.CharField(max_length=30, db_index=True, unique=True)
    monto   = models.DecimalField(max_digits=18, decimal_places=2)
    escaneado = models.BooleanField(_('Escaneado'), default=False)
    fecha_concesion = models.DateField(null=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='credito_cliente')
    moneda  = models.ForeignKey(Moneda, on_delete=models.PROTECT, related_name='credito_moneda')
    oficina = models.ForeignKey(Oficina, on_delete=models.PROTECT, related_name='credito_oficina')
    producto= models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='credito_producto')
    credito_anterior = models.CharField(max_length=60, blank=True)
    history = HistoricalRecords(excluded_fields=['numero', 'monto', 'fecha_concesion', 
        'fecha_ingreso', 'cliente', 'moneda', 'oficina', 'producto', 'credito_anterior'],
        user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        permissions = [
            ("load_credito", "Carga masiva de créditos"),
            ("label_credito", "Permite imprimir etiquetas de los tomos"),
        ]

    def __str__(self):
        return f"{self.numero} - {self.cliente.nombre}"

    def get_credito_anterior(self):
        return self.credito_anterior if self.credito_anterior else '-'

    def view_url(self):
        return reverse('documentos:credito_view', kwargs={'pk': self.id})

    def labels_url(self):
        return reverse('documentos:credito_labels', kwargs={'pk': self.id})

    def cant_tomos(self):
        return Tomo.objects.filter(credito=self, vigente=True).count()

    def esta_escaneado(self):
        return _('Si') if self.escaneado else _('No')

class Solicitante(models.Model):
    '''
        Listado de posibles solicitantes de documentos a Boveda 
    '''
    AREA = [
        ('EXP', _('Expedientes')),
        ('FHA', _('FHA')),
    ]

    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo  = models.PositiveIntegerField(_('Código'))
    nombre  = models.CharField(_('Nombre'), max_length=30, db_index=True)
    area    = models.CharField(_('Area'), choices=AREA, max_length=3, db_index=True) #get_area_display
    extension = models.CharField(_('Extension'), max_length=6, blank=True, default='')
    correo  = models.EmailField(_('Correo'), max_length=60, blank=True, default='')
    gerencia = models.CharField(_('Gerencia'), max_length=60, blank=True, default='')
    vigente = models.BooleanField(_('Estado'), default=True)
    history = HistoricalRecords(
        history_id_field = models.BigAutoField(),
        user_model = settings.AUTH_USER_MODEL,
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['codigo', 'area'], name='unq_codigo_area'),
        ]

    def __str__(self):
        return f'{self.nombre} ({self.codigo})'

    def delete(self):
        self.vigente = not self.vigente
        self.save()

    def hard_delete(self):
        super().delete()

    def get_estado(self):
        return _('Vigente') if self.vigente else _('No Vigente')

    def get_accion(self):
        return 'Inhabilitar' if self.vigente else 'Habilitar'

    def get_accion_tag(self):
        return 'danger' if self.vigente else 'success'

    def list_url(self=None):
        return reverse('documentos:solicitante_list')

    def view_url(self):
        return  reverse('documentos:solicitante_view', kwargs={'pk': self.id})

    def update_url(self):
        return  reverse('documentos:solicitante_update', kwargs={'pk': self.id})

    def delete_url(self):
        return  reverse('documentos:solicitante_delete', kwargs={'pk': self.id})

class Motivo(models.Model):
    '''
        Motivos por los cuales puede solicitarse un documento a bóveda
    '''
    AREA = [
        ('EXP', _('Expedientes')),
        ('FHA', _('FHA')),
    ]

    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre  = models.CharField(_('Nombre'),db_index=True, max_length=30, unique=True) #get_area_display
    area    = models.CharField(_('Area'), choices=AREA, max_length=3, db_index=True)
    demanda = models.BooleanField(_('Demanda'), default=False)
    vigente  = models.BooleanField(_('Estado'), default=True)
    history = HistoricalRecords(
        history_id_field = models.BigAutoField(),
        user_model = settings.AUTH_USER_MODEL,
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nombre', 'area'], name='unq_nombre_area'),
        ]

    def __str__(self):
        return self.nombre

    def delete(self):
        self.vigente = not self.vigente
        self.save()

    def hard_delete(self):
        super().delete()

    def get_es_demanda(self):
        return ('Si') if self.demanda else _('No')

    def get_estado(self):
        return _('Vigente') if self.vigente else _('No Vigente')

    def get_accion(self):
        return 'Inhabilitar' if self.vigente else 'Habilitar'

    def get_accion_tag(self):
        return 'danger' if self.vigente else 'success'

    def list_url(self=None):
        return reverse('documentos:motivo_list')

    def view_url(self):
        return  reverse('documentos:motivo_view', kwargs={'pk': self.id})

    def update_url(self):
        return  reverse('documentos:motivo_update', kwargs={'pk': self.id})

    def delete_url(self):
        return  reverse('documentos:motivo_delete', kwargs={'pk': self.id})

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
#                   INFORMACIÓN EXPEDIENTES
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
class Bodega(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo  = models.CharField(_('Código'), max_length=3, unique=True, 
        help_text=_('Código de 3 caracteres'))
    nombre  = models.CharField(_('Nombre'), max_length=120, unique=True)
    direccion = models.CharField(_('Dirección'), max_length=210)
    vigente = models.BooleanField(_('Estado'), default=True) # para eliminación lógica
    correo_egreso = models.BooleanField(_('Correo por egreso'), default=True)
    correo_traslado = models.BooleanField(_('Correo por traslado'), default=True)
    encargado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, 
        help_text=_('Usuarios en grupos que inicien con "Expedientes"'), 
        verbose_name=_('Encargado'))
    personal = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='bodega_personal', 
        help_text=_('Usuarios en grupos que inicien con "Expedientes"'), 
        verbose_name=_('Personal'))
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        permissions = [
            ("genera_estructura", "Permite generar estructura de la bodega"),
            ("view_estructura", "Permite visualizar la estructura de la bodega"),
        ]

    def __str__(self):
        return self.nombre

    def validate_fields(self, exclude=None):
        qs = Bodega.objects.filter(models.Q(codigo=self.codigo) | models.Q(nombre=self.nombre)).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(_('Código o nombre repetido.'))

    def save(self, *args, **kwargs):
        self.codigo = self.codigo.upper()
        self.nombre = self.nombre.upper()

        self.validate_fields()
        super().save(*args, **kwargs)

    def delete(self):
        self.vigente = not self.vigente
        self.save()

    def hard_delete(self):
        super().delete()
    
    def list_url(self=None):
        return reverse('documentos:bodega_list')

    def view_url(self):
        return reverse('documentos:bodega_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('documentos:bodega_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('documentos:bodega_delete', kwargs={'pk': self.id})

    def get_estado(self):
        return _('Vigente') if self.vigente else _('No Vigente')

    def get_accion(self):
        return _('Inhabilitar') if self.vigente else _('Habilitar')

    def get_accion_tag(self):
        return _('danger') if self.vigente else _('success')


class Estante(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo  = models.CharField(_('Código'), max_length=2, db_index=True, help_text=_('Código máximo de 2 caracteres'))
    vigente = models.BooleanField(_('Estado'), default=True) # para eliminación lógica
    bodega  = models.ForeignKey(Bodega, on_delete=models.PROTECT, related_name='estante_bodega', verbose_name=_('Bodega'))
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['codigo', 'bodega'], name='unq_codigo_bodega'),
        ]
        permissions = [
            ("label_estante", "Permite la impresión de todas las etiquetas del estante"),
        ]

    def __str__(self):
        return f"{self.bodega.codigo}-{self.codigo}"

    def validate_fields(self, exclude=None):
        if not self.codigo.isalpha():
            raise ValidationError(_('El código debe contener únicamente letras.'))

        qs = Estante.objects.filter(codigo=self.codigo, bodega=self.bodega).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(_('Código y bodega repetido.'))

    def save(self, *args, **kwargs):
        self.codigo = self.codigo.upper()

        self.validate_fields()
        super().save(*args, **kwargs)
        
    def list_url():
        return reverse('documentos:estante_list')

    def view_url(self):
        return reverse('documentos:estante_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('documentos:estante_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('documentos:estante_delete', kwargs={'pk': self.id})

    def labels_url(self):
        return reverse('documentos:estante_labels', kwargs={'pk': self.id})

    def get_estado(self):
        return _("Vigente") if self.vigente else _("No Vigente")


class Nivel(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero  = models.PositiveSmallIntegerField(_('Peldaño'), help_text=_('Número del nivel a registrar'))
    vigente = models.BooleanField(_('Estado'), default=True) # para eliminación lógica
    estante = models.ForeignKey(Estante, on_delete=models.PROTECT, related_name='nivel_estante', verbose_name=_('Estante'))
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['estante', 'numero'], name='unq_estante_numero'),
        ]

    def __str__(self):
        return f"{self.estante}-{self.numero:02d}"

    def list_url():
        return reverse('documentos:nivel_list')

    def view_url(self):
        return reverse('documentos:nivel_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('documentos:nivel_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('documentos:nivel_delete', kwargs={'pk': self.id})

    def labels_url(self):
        return reverse('documentos:nivel_labels', kwargs={'pk': self.id})

    def get_estado(self):
        return _("Vigente") if self.vigente else _("No Vigente")


class Posicion(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.PositiveSmallIntegerField(_('Posición'))
    vigente = models.BooleanField(_('Estado'), default=True) # para eliminación lógica
    nivel = models.ForeignKey(Nivel, on_delete=models.PROTECT, related_name='posicion_nivel', verbose_name=_('Nivel'))
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nivel', 'numero'], name='unq_nivel_numero'),
        ]

    def __str__(self):
        return f"{self.nivel}-{self.numero:02d}"

    def list_url():
        return reverse('documentos:posicion_list')

    def view_url(self):
        return reverse('documentos:posicion_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('documentos:posicion_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('documentos:posicion_delete', kwargs={'pk': self.id})

    def get_estado(self):
        return _("Vigente") if self.vigente else _("No Vigente")

    def labels_url(self):
        return reverse('documentos:posicion_labels', kwargs={'pk': self.id})


class Caja(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.PositiveSmallIntegerField(_('Numero'))
    vigente = models.BooleanField(_('Estado'), default=True) # para eliminación lógica
    posicion = models.ForeignKey(Posicion, on_delete=models.PROTECT, related_name='caja_posicion', verbose_name=_('Posición'))
    history = HistoricalRecords(excluded_fields=['numero', 'posicion'], user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['posicion', 'numero'], name='unq_posicion_numero'),
        ]

    def __str__(self):
        return f"{self.posicion}-{self.numero:02d}"

    def validate_fields(self, exclude=None):
        qs = Caja.objects.filter(numero=self.numero, posicion=self.posicion).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(_('Posicion y caja repetida.'))

    def save(self, *args, **kwargs):
        self.validate_fields()
        super().save(*args, **kwargs)

    def delete(self):
        self.vigente = not self.vigente
        self.save()

    def hard_delete(self):
        super().delete()
    
    def list_url():
        return reverse('documentos:caja_list')

    def view_url(self):
        return reverse('documentos:caja_view', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('documentos:caja_delete', kwargs={'pk': self.id})

    def get_estado(self):
        return _("Vigente") if self.vigente else _("No Vigente")

    def get_accion(self):
        return _('Inhabilitar') if self.vigente else _('Habilitar')

    def get_accion_tag(self):
        return _('danger') if self.vigente else _('success')

    def labels_url(self):
        return reverse('documentos:caja_labels', kwargs={'pk': self.id})

    def get_tomos(self):
        return Tomo.objects.filter(caja=self).order_by('-fecha_modificacion')\
            .prefetch_related('credito')


class Tomo(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero  = models.PositiveSmallIntegerField()
    vigente = models.BooleanField(default=True)
    fecha_modificacion = models.DateTimeField(_('Fecha'), auto_now=True)
    comentario = models.TextField()
    credito = models.ForeignKey(Credito, on_delete=models.PROTECT, related_name='tomo_credito')
    caja    = models.ForeignKey(Caja, on_delete=models.PROTECT, null=True, related_name='tomo_caja')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Usuario'), related_name='tomo_usuario')
    history = HistoricalRecords(
        history_id_field = models.BigAutoField(),
        excluded_fields=['numero', 'credito', 'usuario'],
        user_model=settings.AUTH_USER_MODEL,
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['credito', 'numero'], name='unq_credito_numero'),
        ]
        indexes = [
            models.Index(fields=['fecha_modificacion']),
            models.Index(fields=['numero']),
        ]

    def __str__(self):
        return "{}-{}".format(self.credito.numero, self.numero)

    def id_as_string(self):
        return str(self.id)

    def view_credito(self):
        return reverse('documentos:credito_view', kwargs={'pk': self.credito.id})

    def envio_url():
        return reverse('documentos:envio_tomo')

    def egreso_url(self):
        return reverse('documentos:egreso_tomo', kwargs={'pk': self.id})

    def labels_url(self):
        return reverse('documentos:tomo_labels', kwargs={'pk': self.id})

    def get_posicion(self):
        return Caja.objects.filter(id=self.caja.id, tomo_caja__fecha_modificacion__gte=self.fecha_modificacion).count()


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
#                   INFORMACIÓN EXPEDIENTES
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
#                   INFORMACIÓN FHA
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### 
class EncargadoDocumentos(models.Model):
    recibe_correos  = models.BooleanField(_("Encargado que recibe correos"), default=False)
    usuario         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_('Usuario Solicitante'))

class DocumentoFHA(models.Model):
    ''' 
        Documentos almacenados en Bóveda por el FHA
    '''
    TIPO_DOCUMENTO_FHA = [
        ('CED', _('Cédula')),
        ('SEG', _('Seguro')),
        ('ESC', _('Escritura')),
    ]

    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha   = models.DateField(_('Fecha'), auto_now=True)
    tipo    = models.CharField(_('Tipo'), max_length=3,choices=TIPO_DOCUMENTO_FHA) #get_tipo_display
    numero  = models.CharField(_('Número'), max_length=30, db_index=True)
    ubicacion = models.CharField(_('Ubicación'), max_length=12, db_index=True)
    poliza  = models.CharField(_('Póliza de Ingreso'), max_length=12, db_index=True, default='')
    vigente = models.BooleanField(_('Estado'), default=True)
    credito = models.ForeignKey(Credito, verbose_name=_('Crédito'), on_delete=models.PROTECT)
    history = HistoricalRecords(
        history_id_field = models.BigAutoField(),
        excluded_fields = ['fecha', 'credito', 'tipo', 'numero'],
        user_model = settings.AUTH_USER_MODEL,
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['credito', 'tipo', 'numero'], name='unq_credito_tipo_numero'),
        ]
        indexes = [
            models.Index(fields=['tipo', 'numero']),
        ]

    def __str__(self):
        return f'{self.credito}, {self.tipo}: {self.numero}'

    def delete(self):
        self.vigente = not self.vigente
        self.save()

    def hard_delete(self):
        super().delete()

    def get_accion(self):
        return 'Inhabilitar' if self.vigente else 'Habilitar'

    def get_accion_tag(self):
        return 'danger' if self.vigente else 'success'

    def delete_url(self):
        return  reverse('documentos:documentofha_delete', kwargs={'pk': self.id})
    
    def get_documento(self):
        return f'{self.tipo}: {self.numero}'

    def get_estado(self):
        return _('Vigente') if self.vigente else _('No Vigente')

    def existe_solicitud(self):
        return True if self.solicitudfha_set.filter(vigente=True) else False

    def list_url(self=None):
        return self.credito.view_url()

    def find_solicitud(self):
        if self and self.solicitudfha_set.filter(vigente=True, fecha_egreso__isnull=True):
            return reverse('documentos:solicitudfha_list')
        else:
            return reverse('documentos:solicitudfhafuera_list')

class SolicitudFHA(models.Model):
    '''
        Ciclo de vida de la solicitud
    '''
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fecha_solicitud = models.DateField(_('Fecha'), db_index=True, auto_now_add=True)
    bufete          = models.CharField(_('Bufete'), max_length=30, default='')
    fecha_egreso    = models.DateField(_('Egreso de Bóveda'), null=True)
    poliza_egreso   = models.CharField(_('Póliza de Egreso'), max_length=12)
    fecha_entrega   = models.DateField(_('Entrega a solicitante'), null=True)
    fecha_devolucion= models.DateField(_('Devolución de solicitante'), null=True)
    regreso_boveda  = models.BooleanField(default=False)
    vigente         = models.BooleanField(default=True)
    documento       = models.ForeignKey(DocumentoFHA, verbose_name=_('Documento'), on_delete=models.PROTECT)
    solicitante     = models.ForeignKey(Solicitante, verbose_name=_('Solicitante'), on_delete=models.PROTECT)
    motivo          = models.ForeignKey(Motivo, verbose_name=_('Motivo'), on_delete=models.PROTECT)
    usuario         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name=_('Usuario'))
    history = HistoricalRecords(
        history_id_field = models.BigAutoField(),
        excluded_fields = ['fecha_solicitud', 'bufete', 'fecha_egreso', 'poliza_egreso', 'regreso_boveda', 'vigente',
        'documento', 'solicitante', 'motivo', 'usuario'],
        user_model = settings.AUTH_USER_MODEL,
        )

    def __str__(self):
        return f'{self.fecha_solicitud} / {self.motivo}'

    def delete(self):
        self.vigente = False
        self.save()

    def hard_delete(self):
        super().delete()

    def get_accion(self):
        return 'Inhabilitar' if self.vigente else 'Habilitar'

    def get_accion_tag(self):
        return 'danger' if self.vigente else 'success'

    def list_url(self=None):
        return reverse('documentos:solicitudfha_list')

    def listfueraboveda_url(self=None):
        return reverse('documentos:solicitudfhafuera_list')

    def delete_url(self):
        return reverse('documentos:solicitudfha_delete', kwargs={'pk': self.id})