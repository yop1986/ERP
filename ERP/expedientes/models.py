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
    codigo  = models.CharField(_('Código'), max_length=3, unique=True, help_text=_('Código de 3 caracteres'))
    nombre  = models.CharField(_('Nombre'), max_length=30, unique=True)
    direccion = models.CharField(_('Dirección'), max_length=120)
    vigente = models.BooleanField(_('Estado'), default=True) # para eliminación lógica
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
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

    def detail_url(self):
        return reverse('expedientes:bodega_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:bodega_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:bodega_delete', kwargs={'pk': self.id})

    def get_estado(self):
        return _("Vigente") if self.vigente else _("No Vigente")


class Estante(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo  = models.CharField(max_length=2, db_index=True, help_text=_('Código máximo de 2 caracteres'))
    vigente = models.BooleanField(default=True) # para eliminación lógica
    bodega  = models.ForeignKey(Bodega, on_delete=models.PROTECT, related_name='estante_bodega')
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['codigo', 'bodega'], name='unq_codigo_bodega'),
        ]
        permissions = [
            ("label_estante", "Can print the labels from estante"),
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

    def detail_url(self):
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
    numero  = models.PositiveSmallIntegerField(help_text=_('Número del nivel a registrar'))
    vigente = models.BooleanField(default=True) # para eliminación lógica
    estante = models.ForeignKey(Estante, on_delete=models.PROTECT, related_name='nivel_estante')
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['estante', 'numero'], name='unq_estante_numero'),
        ]
        permissions = [
            ("label_nivel", "Can print the labels fron nivel"),
        ]

    def __str__(self):
        return f"{self.estante}-{self.numero:02d}"

    def validate_fields(self, exclude=None):
        qs = Nivel.objects.filter(numero=self.numero, estante=self.estante).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(_('Nivel y estante repetido.'))

    def save(self, *args, **kwargs):
        self.validate_fields()
        super().save(*args, **kwargs)

    def list_url():
        return reverse('expedientes:nivel_list')

    def detail_url(self):
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
    numero = models.PositiveSmallIntegerField()
    vigente = models.BooleanField(default=True) # para eliminación lógica
    nivel = models.ForeignKey(Nivel, on_delete=models.PROTECT, related_name='posicion_nivel')
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nivel', 'numero'], name='unq_nivel_numero'),
        ]
        permissions = [
            ("label_posicion", "Can print the labels from posicion"),
        ]

    def __str__(self):
        return f"{self.nivel}-{self.numero:02d}"

    def validate_fields(self, exclude=None):
        qs = Posicion.objects.filter(numero=self.numero, nivel=self.nivel).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(_('Nivel y posición repetida.'))

    def save(self, *args, **kwargs):
        self.validate_fields()
        super().save(*args, **kwargs)

    def list_url():
        return reverse('expedientes:posicion_list')

    def detail_url(self):
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
    numero = models.PositiveSmallIntegerField()
    vigente = models.BooleanField(default=True) # para eliminación lógica
    posicion = models.ForeignKey(Posicion, on_delete=models.PROTECT, related_name='caja_posicion')
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['posicion', 'numero'], name='unq_posicion_numero'),
        ]
        permissions = [
            ("label_caja", "Can print the labels from caja"),
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

    def list_url():
        return reverse('expedientes:caja_list')

    def detail_url(self):
        return reverse('expedientes:caja_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:caja_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:caja_delete', kwargs={'pk': self.id})

    def get_estado(self):
        return _("Vigente") if self.vigente else _("No Vigente")

    def labels_url(self):
        return reverse('expedientes:caja_labels', kwargs={'pk': self.id})


class Cliente(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.PositiveIntegerField(db_index=True, unique=True)
    nombre = models.CharField(max_length=90)
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def validate_fields(self, exclude=None):
        qs = Cliente.objects.filter(codigo=self.codigo).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(_('Código ya existe.'))

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper()

        self.validate_fields()
        super().save(*args, **kwargs)

    def list_url():
        return reverse('expedientes:cliente_list')

    def detail_url(self):
        return reverse('expedientes:cliente_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:cliente_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:cliente_delete', kwargs={'pk': self.id})

    def get_tiene_hijos(self):
        return True if self.credito_cliente.count()>0 else False

    def get_hijos(self):
        return self.credito_cliente.all()


class Moneda(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(max_length=21, unique=True)
    simbolo = models.CharField(max_length=1, unique=True, blank=True, null=True)
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    def __str__(self):
        return f"{self.descripcion} ({self.simbolo})"

    def validate_fields(self, exclude=None):
        qs = Moneda.objects.filter(models.Q(descripcion=self.descripcion) | models.Q(simbolo=self.simbolo)).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(_('Descripción o simbolo ya existe.'))

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        self.simbolo = self.simbolo.upper() if self.simbolo else ''

        self.validate_fields()
        super().save(*args, **kwargs)

    def list_url():
        return reverse('expedientes:moneda_list')

    def detail_url(self):
        return reverse('expedientes:moneda_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:moneda_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:moneda_delete', kwargs={'pk': self.id})


class Producto(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descripcion = models.CharField(max_length=12, unique=True)
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.descripcion

    def validate_fields(self, exclude=None):
        qs = Moneda.objects.filter(descripcion=self.descripcion).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(_('Producto ya existe.'))

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        
        self.validate_fields()
        super().save(*args, **kwargs)

    def list_url():
        return reverse('expedientes:producto_list')

    def detail_url(self):
        return reverse('expedientes:producto_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:producto_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:producto_delete', kwargs={'pk': self.id})


class Oficina(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.PositiveIntegerField(db_index=True, unique=True)
    descripcion = models.CharField(max_length=60)
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)

    def __str__(self):
        return f"{str(self.numero).zfill(4)} - {self.descripcion}"

    def validate_fields(self, exclude=None):
        qs = Oficina.objects.filter(models.Q(descripcion=self.descripcion) | models.Q(numero=self.numero)).exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(_('Número u oficina ya existe.'))

    def save(self, *args, **kwargs):
        self.descripcion = self.descripcion.upper()
        
        self.validate_fields()
        super().save(*args, **kwargs)

    def list_url():
        return reverse('expedientes:oficina_list')

    def detail_url(self):
        return reverse('expedientes:oficina_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:oficina_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:oficina_delete', kwargs={'pk': self.id})


class Credito(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero  = models.CharField(max_length=18, db_index=True, unique=True)
    monto   = models.DecimalField(max_digits=18, decimal_places=2)
    fecha_concesion = models.DateField(null=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='credito_cliente')
    moneda  = models.ForeignKey(Moneda, on_delete=models.PROTECT, related_name='credito_moneda')
    oficina = models.ForeignKey(Oficina, on_delete=models.PROTECT, related_name='credito_oficina')
    producto= models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='credito_producto')
    history = HistoricalRecords(user_model=settings.AUTH_USER_MODEL)
    
    class Meta:
        permissions = [
            ("load_credito", "Masive load of credits"),
        ]

    def __str__(self):
        return f"{self.numero} - {self.cliente.nombre}"

    def list_url():
        return reverse('expedientes:credito_list')

    def detail_url(self):
        return reverse('expedientes:credito_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:credito_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:credito_delete', kwargs={'pk': self.id})

    def get_tiene_hijos(self):
        return True if self.folio_set.count()>0 else False

    def get_hijos(self):
        return self.folio_credito.filter(vigente=True)


class Folio(models.Model):
    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero  = models.PositiveSmallIntegerField()
    vigente = models.BooleanField(default=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    comentario = models.TextField()
    credito = models.ForeignKey(Credito, on_delete=models.PROTECT, related_name='folio_credito')
    caja    = models.ForeignKey(Caja, on_delete=models.PROTECT, null=True, related_name='folio_caja')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Usuario'), related_name='folio_usuario')
    history = HistoricalRecords(
        history_id_field = models.BigAutoField(),
        excluded_fields=['numero', 'credito', 'comentario', 'fecha_modificacion', 'usuario'],
        user_model=settings.AUTH_USER_MODEL,
        history_change_reason_field=models.TextField(null=True)
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['credito', 'numero'], name='unq_credito_numero'),
        ]

    def __str__(self):
        return "{}-{}".format(self.credito.numero, self.numero)

    def list_url():
        return reverse('expedientes:folio_list')

    def detail_url(self):
        return reverse('expedientes:folio_view', kwargs={'pk': self.id})

    def update_url(self):
        return reverse('expedientes:folio_update', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse('expedientes:folio_delete', kwargs={'pk': self.id})

    def get_ubicacion(self):
        return self.caja if self.caja else self.comentario if self.comentario else ''

    def get_fecha_modificacion(self):
        return self.fecha_modificacion if self.fecha_modificacion else None

    def delete(self):
        self.vigente = False
        super(Folio, self).delete()
