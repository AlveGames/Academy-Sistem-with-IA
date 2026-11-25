# =====================================================================
# core/models.py · el molde que heredan TODOS los modelos del sistema
# =====================================================================
from django.contrib.auth.models import User
from django.db import models


class ModeloBase(models.Model):
    # Quién registró o modificó el registro por última vez.
    # SET_NULL: si se borra el usuario, el registro NO se borra; este campo queda vacío.
    # editable=False: no aparece en los formularios (lo llena la vista o el admin).
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, editable=False,
        # %(app_label)s y %(class)s se reemplazan por la app y el modelo:
        # así cada modelo tiene un nombre de vuelta distinto (ej: academico_estudiante_registrados)
        related_name="%(app_label)s_%(class)s_registrados",
        verbose_name="Registrado por",
    )
    fecha_creacion = models.DateTimeField("Fecha de creación", auto_now_add=True)        # se pone solo al crear
    fecha_modificacion = models.DateTimeField("Última modificación", auto_now=True)      # se actualiza en cada save()

    class Meta:
        abstract = True   # es un molde: NO crea tabla, solo presta sus campos a quien lo herede
