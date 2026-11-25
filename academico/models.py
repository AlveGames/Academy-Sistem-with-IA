# =====================================================================
# academico/models.py · Sistema académico
# Orden: estructura (Universidad → Facultad → Carrera) → catálogo (Semestre, Periodo, Curso)
#        → personas (Profesor, Estudiante) → oferta (Seccion) → proceso (Matricula → Nota)
# =====================================================================
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from core.models import ModeloBase

# ---------------------------------------------------------------------
# CONSTANTES DEL NEGOCIO
# ---------------------------------------------------------------------
NOTA_MINIMA_APROBACION = Decimal("70")   # se aprueba con 70 o más
NOTA_MAXIMA = Decimal("100")
# Lista de validadores que reutilizan n1, n2 y n3: 0 ≤ nota ≤ 100
VALIDAR_NOTA = [MinValueValidator(Decimal("0")), MaxValueValidator(NOTA_MAXIMA)]


# ---------------------------------------------------------------------
# OPCIONES FIJAS (choices): (valor que se guarda, texto que se muestra)
# ---------------------------------------------------------------------
class Jornada(models.TextChoices):
    DIURNA = "diurna", "Diurna"
    NOCTURNA = "nocturna", "Nocturna"


class EstadoNota(models.TextChoices):
    APROBADO = "aprobado", "Aprobado"
    REPROBADO = "reprobado", "Reprobado"


# =====================================================================
# 1. ESTRUCTURA: Universidad 1:N Facultad 1:N Carrera
# =====================================================================
class Universidad(ModeloBase):
    nombre = models.CharField(max_length=150, unique=True)
    siglas = models.CharField(max_length=20)                           # Ej: UG, ESPOL
    ciudad = models.CharField(max_length=80)
    logo = models.ImageField(upload_to="universidades/", blank=True)   # opcional; sale en los comprobantes PDF

    class Meta:
        verbose_name = "Universidad"
        verbose_name_plural = "Universidades"
        ordering = ["nombre"]

    def __str__(self):
        return self.siglas


class Facultad(ModeloBase):
    # PROTECT: no deja borrar una universidad que todavía tiene facultades
    universidad = models.ForeignKey(Universidad, on_delete=models.PROTECT, related_name="facultades")   # 1:N
    nombre = models.CharField(max_length=150)
    decano = models.CharField(max_length=150, blank=True)              # opcional

    class Meta:
        verbose_name = "Facultad"
        verbose_name_plural = "Facultades"
        ordering = ["nombre"]
        constraints = [   # el mismo nombre puede existir en otra universidad, pero no dos veces en la misma
            models.UniqueConstraint(fields=["universidad", "nombre"], name="facultad_unica_por_universidad"),
        ]

    def __str__(self):
        return self.nombre


class Carrera(ModeloBase):
    facultad = models.ForeignKey(Facultad, on_delete=models.PROTECT, related_name="carreras")   # 1:N
    codigo = models.CharField("Código", max_length=10, unique=True)   # Ej: SOF
    nombre = models.CharField(max_length=150)
    duracion_semestres = models.PositiveSmallIntegerField("Duración (semestres)", default=8)

    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# =====================================================================
# 2. CATÁLOGO: Semestre, Periodo y Curso
# =====================================================================
class Semestre(ModeloBase):
    numero = models.PositiveSmallIntegerField(unique=True, validators=[MinValueValidator(1), MaxValueValidator(12)])
    nombre = models.CharField(max_length=30)                           # Ej: Primer semestre

    class Meta:
        verbose_name = "Semestre"
        verbose_name_plural = "Semestres"
        ordering = ["numero"]

    def __str__(self):
        return self.nombre


class Periodo(ModeloBase):
    nombre = models.CharField(max_length=20, unique=True)              # Ej: 2026-1
    fecha_inicio = models.DateField("Fecha de inicio")
    fecha_fin = models.DateField("Fecha de fin")
    activo = models.BooleanField(default=False)                        # el periodo en el que se matricula

    class Meta:
        verbose_name = "Periodo"
        verbose_name_plural = "Periodos"
        ordering = ["-fecha_inicio"]                                   # el "-" = el más reciente primero

    def __str__(self):
        return self.nombre

    def clean(self):
        """Validación que mira VARIOS campos juntos (la llaman los formularios solos)."""
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            # el diccionario pone el error debajo del campo fecha_fin en el formulario
            raise ValidationError({"fecha_fin": "La fecha de fin debe ser posterior a la de inicio."})


class Curso(ModeloBase):                                               # la asignatura (materia)
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT, related_name="cursos")      # 1:N
    semestre = models.ForeignKey(Semestre, on_delete=models.PROTECT, related_name="cursos")    # 1:N
    codigo = models.CharField("Código", max_length=12, unique=True)   # Ej: SOF-101
    nombre = models.CharField(max_length=150)
    creditos = models.PositiveSmallIntegerField("Créditos", default=3)

    class Meta:
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"
        ordering = ["carrera", "semestre__numero", "nombre"]           # "__" = campo de la tabla relacionada

    def __str__(self):
        return f"{self.codigo} · {self.nombre}"


# =====================================================================
# 3. PERSONAS: Profesor y Estudiante
# =====================================================================
class Profesor(ModeloBase):
    cedula = models.CharField("Cédula", max_length=10, unique=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    email = models.EmailField("Correo", blank=True)
    titulo = models.CharField("Título", max_length=120, blank=True)   # Ej: Mg. en Software

    class Meta:
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"


class Estudiante(ModeloBase):
    cedula = models.CharField("Cédula", max_length=10, unique=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    email = models.EmailField("Correo", blank=True)
    telefono = models.CharField("Teléfono", max_length=15, blank=True)
    fecha_nacimiento = models.DateField("Fecha de nacimiento", null=True, blank=True)   # opcional
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT, related_name="estudiantes")   # 1:N
    foto = models.ImageField(upload_to="estudiantes/", blank=True)    # opcional; se guarda en media/estudiantes/

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"

    @property                       # se usa como campo: estudiante.nombre_completo (sin paréntesis)
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


# =====================================================================
# 4. OFERTA: la Sección es UN curso, en UN periodo, con UN profesor, en UNA jornada
# =====================================================================
class Seccion(ModeloBase):
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name="secciones")
    periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, related_name="secciones")
    profesor = models.ForeignKey(Profesor, on_delete=models.PROTECT, related_name="secciones")
    paralelo = models.CharField(max_length=2, default="A")             # A, B, C...
    jornada = models.CharField(max_length=10, choices=Jornada.choices, default=Jornada.DIURNA)
    cupo = models.PositiveSmallIntegerField(default=30)
    # N:M con Estudiante A TRAVÉS de Matricula: la tabla intermedia la escribimos nosotros
    # porque guarda datos propios (la fecha y, después, la nota)
    estudiantes = models.ManyToManyField("Estudiante", through="Matricula", related_name="secciones")

    class Meta:
        verbose_name = "Sección"
        verbose_name_plural = "Secciones"
        ordering = ["periodo", "curso", "paralelo"]
        constraints = [   # no se puede abrir dos veces el mismo curso, periodo, paralelo y jornada
            models.UniqueConstraint(fields=["curso", "periodo", "paralelo", "jornada"], name="seccion_unica"),
        ]

    def __str__(self):
        # get_jornada_display() devuelve el texto bonito del choice ("Nocturna" en vez de "nocturna")
        return f"{self.curso.codigo} {self.paralelo} · {self.get_jornada_display()} · {self.periodo}"

    @property
    def inscritos(self):
        """Cuántos estudiantes están matriculados en esta sección."""
        return self.matriculas.count()


# =====================================================================
# 5. PROCESO: Matricula (N:M Estudiante–Seccion con datos) y Nota (1:1 con Matricula)
# =====================================================================
class Matricula(ModeloBase):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT, related_name="matriculas")
    seccion = models.ForeignKey(Seccion, on_delete=models.PROTECT, related_name="matriculas")
    fecha = models.DateField(default=timezone.localdate)   # sin paréntesis: Django la llama al crear cada matrícula

    class Meta:
        verbose_name = "Matrícula"
        verbose_name_plural = "Matrículas"
        ordering = ["-fecha"]
        constraints = [   # un estudiante no se matricula dos veces en la misma sección
            models.UniqueConstraint(fields=["estudiante", "seccion"], name="matricula_unica"),
        ]

    def __str__(self):
        return f"{self.estudiante} → {self.seccion}"

    def clean(self):
        """Reglas del negocio que miran OTRAS tablas."""
        if not self.estudiante_id or not self.seccion_id:   # si falta alguno, ya lo avisa su propio campo
            return
        # Regla 1: el curso de la sección debe ser de la carrera del estudiante
        if self.seccion.curso.carrera_id != self.estudiante.carrera_id:
            raise ValidationError("El curso no pertenece a la carrera del estudiante.")
        # Regla 2: la sección debe tener cupo (exclude(pk=self.pk) para no contarse a sí misma al editar)
        ocupados = self.seccion.matriculas.exclude(pk=self.pk).count()
        if ocupados >= self.seccion.cupo:
            raise ValidationError(f"La sección no tiene cupo ({self.seccion.cupo} estudiantes).")


class Nota(ModeloBase):
    # 1:1: cada matrícula tiene como máximo UNA nota. CASCADE: si se borra la matrícula, se borra su nota
    matricula = models.OneToOneField(Matricula, on_delete=models.CASCADE, related_name="nota")
    n1 = models.DecimalField("Nota 1", max_digits=5, decimal_places=2, default=0, validators=VALIDAR_NOTA)
    n2 = models.DecimalField("Nota 2", max_digits=5, decimal_places=2, default=0, validators=VALIDAR_NOTA)
    n3 = models.DecimalField("Nota 3", max_digits=5, decimal_places=2, default=0, validators=VALIDAR_NOTA)
    # Calculados en save(): se guardan para poder FILTRAR y EXPORTAR por ellos (ej: "todos los reprobados")
    promedio = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    estado = models.CharField(max_length=10, choices=EstadoNota.choices, default=EstadoNota.REPROBADO, editable=False)

    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"
        ordering = ["matricula__estudiante__apellidos"]   # ordenadas por el apellido del estudiante

    def __str__(self):
        return f"{self.matricula.estudiante} · {self.promedio} ({self.get_estado_display()})"

    def save(self, *args, **kwargs):
        """Antes de guardar: calcula el promedio y decide si aprueba."""
        # Decimal(...) por si llegan como int o texto; quantize = redondear a 2 decimales
        total = Decimal(self.n1) + Decimal(self.n2) + Decimal(self.n3)
        self.promedio = (total / 3).quantize(Decimal("0.01"))
        self.estado = EstadoNota.APROBADO if self.promedio >= NOTA_MINIMA_APROBACION else EstadoNota.REPROBADO
        super().save(*args, **kwargs)   # ahora sí: INSERT o UPDATE en la base de datos
