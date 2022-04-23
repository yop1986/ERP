import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from simple_history.models import HistoricalRecords

# Create your models here.
class Bodega(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo  = models.CharField(_('Código'), max_length=3, unique=True, 
        help_text=_('Código de 3 caracteres'))
    nombre  = models.CharField(_('Nombre'), max_length=30, unique=True)
    direccion = models.CharField(_('Dirección'), max_length=120)
    vigente = models.BooleanField(_('Estado'), default=True) # para eliminación lógica
    correo_egreso = models.BooleanField(_('Correo por egreso'), default=True)
    correo_traslado = models.BooleanField(_('Correo por traslado'), default=True)
    encargado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
        null=True, blank=True, help_text=_('Usuarios en grupos que inicien con "Expedientes"'), 
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
        return reverse('expedientes:bodega_list')

    def view_url(self):
        return reverse('expedientes:bodega_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:bodega_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:bodega_delete', kwargs={'pk': self.id})

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
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
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
        return reverse('expedientes:estante_list')

    def view_url(self):
        return reverse('expedientes:estante_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:estante_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:estante_delete', kwargs={'pk': self.id})

    def labels_url(self):
        return reverse('expedientes:estante_labels', kwargs={'pk': self.id})

    def get_estado(self):
        return _("Vigente") if self.vigente else _("No Vigente")


class Nivel(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero  = models.PositiveSmallIntegerField(_('Peldaño'), help_text=_('Número del nivel a registrar'))
    vigente = models.BooleanField(_('Estado'), default=True) # para eliminación lógica
    estante = models.ForeignKey(Estante, on_delete=models.PROTECT, related_name='nivel_estante', verbose_name=_('Estante'))
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['estante', 'numero'], name='unq_estante_numero'),
        ]
        permissions = [
            ("label_nivel", "Permite la impresión de todas las etiquetas del nivel"),
        ]

    def __str__(self):
        return f"{self.estante}-{self.numero:02d}"

    def list_url():
        return reverse('expedientes:nivel_list')

    def view_url(self):
        return reverse('expedientes:nivel_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:nivel_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:nivel_delete', kwargs={'pk': self.id})

    def labels_url(self):
        return reverse('expedientes:nivel_labels', kwargs={'pk': self.id})

    def get_estado(self):
        return _("Vigente") if self.vigente else _("No Vigente")


class Posicion(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.PositiveSmallIntegerField(_('Posición'))
    vigente = models.BooleanField(_('Estado'), default=True) # para eliminación lógica
    nivel = models.ForeignKey(Nivel, on_delete=models.PROTECT, related_name='posicion_nivel', verbose_name=_('Nivel'))
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nivel', 'numero'], name='unq_nivel_numero'),
        ]
        permissions = [
            ("label_posicion", "Permite la impresión de todas las etiquetas de la posición"),
        ]

    def __str__(self):
        return f"{self.nivel}-{self.numero:02d}"

    def list_url():
        return reverse('expedientes:posicion_list')

    def view_url(self):
        return reverse('expedientes:posicion_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:posicion_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:posicion_delete', kwargs={'pk': self.id})

    def get_estado(self):
        return _("Vigente") if self.vigente else _("No Vigente")

    def labels_url(self):
        return reverse('expedientes:posicion_labels', kwargs={'pk': self.id})


class Caja(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.PositiveSmallIntegerField(_('Numero'))
    vigente = models.BooleanField(_('Estado'), default=True) # para eliminación lógica
    posicion = models.ForeignKey(Posicion, on_delete=models.PROTECT, related_name='caja_posicion', verbose_name=_('Posición'))
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['posicion', 'numero'], name='unq_posicion_numero'),
        ]
        permissions = [
            ("label_caja", "Permite la impresión de la etiqueta de la caja"),
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
        return reverse('expedientes:caja_list')

    def view_url(self):
        return reverse('expedientes:caja_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:caja_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:caja_delete', kwargs={'pk': self.id})

    def get_estado(self):
        return _("Vigente") if self.vigente else _("No Vigente")

    def get_accion(self):
        return _('Inhabilitar') if self.vigente else _('Habilitar')

    def get_accion_tag(self):
        return _('danger') if self.vigente else _('success')

    def labels_url(self):
        return reverse('expedientes:caja_labels', kwargs={'pk': self.id})

    def get_tomos(self):
        return Tomo.objects.filter(caja=self).order_by('-fecha_modificacion')\
            .prefetch_related('credito')


class Cliente(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.PositiveIntegerField(db_index=True, unique=True)
    nombre = models.CharField(max_length=90)
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Moneda(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(max_length=21, unique=True)
    simbolo = models.CharField(max_length=1, unique=True, blank=True, null=True)
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    def __str__(self):
        return f"{self.descripcion} ({self.simbolo})"

    
class Producto(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(max_length=12, unique=True)
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.descripcion

    
class Oficina(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.PositiveIntegerField(db_index=True, unique=True)
    descripcion = models.CharField(max_length=60)
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return f"{str(self.numero).zfill(4)} - {self.descripcion}"

    
class Credito(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero  = models.CharField(max_length=18, db_index=True, unique=True)
    monto   = models.DecimalField(max_digits=18, decimal_places=2)
    escaneado = models.BooleanField(_('Escaneado'), default=False)
    fecha_concesion = models.DateField(null=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='credito_cliente')
    moneda  = models.ForeignKey(Moneda, on_delete=models.PROTECT, related_name='credito_moneda')
    oficina = models.ForeignKey(Oficina, on_delete=models.PROTECT, related_name='credito_oficina')
    producto= models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='credito_producto')
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        permissions = [
            ("load_credito", "Carga masiva de créditos"),
            ("label_credito", "Permite imprimir etiquetas de los tomos"),
        ]

    def __str__(self):
        return f"{self.numero} - {self.cliente.nombre}"

    def view_url(self):
        return reverse('expedientes:credito_view', kwargs={'pk': self.id})

    def labels_url(self):
        return reverse('expedientes:credito_labels', kwargs={'pk': self.id})

    def cant_tomos(self):
        return Tomo.objects.filter(credito=self, vigente=True).count()

    def esta_escaneado(self):
        return _('Si') if self.escaneado else _('No')


class Tomo(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero  = models.PositiveSmallIntegerField()
    vigente = models.BooleanField(default=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    comentario = models.TextField()
    credito = models.ForeignKey(Credito, on_delete=models.PROTECT, related_name='tomo_credito')
    caja    = models.ForeignKey(Caja, on_delete=models.PROTECT, null=True, related_name='tomo_caja')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Usuario'), related_name='tomo_usuario')
    history = HistoricalRecords(
        history_id_field = models.BigAutoField(),
        excluded_fields=['numero', 'credito'],
        user_model=settings.AUTH_USER_MODEL,
        #history_change_reason_field=models.TextField(null=True)
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['credito', 'numero'], name='unq_credito_numero'),
        ]
        indexes = [
            models.Index(fields=['fecha_modificacion'])
        ]
        permissions = [
            ("label_tomo", "Permite imprimir etiquetas de los tomos"),
        ]

    def __str__(self):
        return "{}-{}".format(self.credito.numero, self.numero)

    def view_credito(self):
        return reverse('expedientes:credito_view', kwargs={'pk': self.credito.id})

    def envio_url():
        return reverse('expedientes:envio_tomo')

    def egreso_url(self):
        return reverse('expedientes:egreso_tomo', kwargs={'pk': self.id})

    def remover_url(self):
        return reverse('expedientes:remover_tomo', kwargs={'pk': self.id})

    def labels_url(self):
        return reverse('expedientes:tomo_labels', kwargs={'pk': self.id})

    def get_posicion(self):
        return Caja.objects.filter(id=self.caja.id, tomo_caja__fecha_modificacion__gte=self.fecha_modificacion).count()

