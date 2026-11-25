# =====================================================================
# academico/admin.py · panel de administración (/admin/)
# =====================================================================
from django.contrib import admin

from .models import (
    Carrera, Curso, Estudiante, Facultad, Matricula, Nota,
    Periodo, Profesor, Seccion, Semestre, Universidad,
)

# Campos de ModeloBase: los llena el sistema, nadie los escribe a mano
CAMPOS_AUDITORIA = ("user", "fecha_creacion", "fecha_modificacion")


class BaseAdmin(admin.ModelAdmin):
    """Molde para todos los admin: muestra la auditoría y guarda quién hizo el cambio."""
    readonly_fields = CAMPOS_AUDITORIA   # se ven en el formulario pero no se pueden editar
    list_per_page = 20                   # 20 filas por página en los listados

    def save_model(self, request, obj, form, change):
        # request.user = el usuario que inició sesión en el admin
        obj.user = request.user
        super().save_model(request, obj, form, change)   # ahora sí guarda en la base

    def save_formset(self, request, form, formset, change):
        # Lo mismo para los inline (ej: la Nota dentro de la Matrícula)
        objetos = formset.save(commit=False)   # commit=False: todavía NO guarda
        for obj in objetos:
            obj.user = request.user
            obj.save()                         # aquí Nota.save() calcula promedio y estado
        for obj in formset.deleted_objects:    # los que marcaron "Eliminar"
            obj.delete()
        formset.save_m2m()


# ---------------------------------------------------------------------
# 1. ESTRUCTURA
# ---------------------------------------------------------------------
@admin.register(Universidad)   # el decorador hace lo mismo que admin.site.register(Universidad, UniversidadAdmin)
class UniversidadAdmin(BaseAdmin):
    list_display = ("siglas", "nombre", "ciudad")         # columnas del listado
    search_fields = ("nombre", "siglas", "ciudad")        # caja de búsqueda
    list_filter = ("ciudad",)                             # filtros de la derecha (la coma lo hace tupla)


@admin.register(Facultad)
class FacultadAdmin(BaseAdmin):
    list_display = ("nombre", "universidad", "decano")
    search_fields = ("nombre", "decano", "universidad__siglas")   # "__" busca en la tabla relacionada
    list_filter = ("universidad",)


@admin.register(Carrera)
class CarreraAdmin(BaseAdmin):
    list_display = ("codigo", "nombre", "facultad", "duracion_semestres")
    search_fields = ("codigo", "nombre")
    list_filter = ("facultad__universidad", "facultad")


# ---------------------------------------------------------------------
# 2. CATÁLOGO
# ---------------------------------------------------------------------
@admin.register(Semestre)
class SemestreAdmin(BaseAdmin):
    list_display = ("numero", "nombre")
    search_fields = ("nombre",)


@admin.register(Periodo)
class PeriodoAdmin(BaseAdmin):
    list_display = ("nombre", "fecha_inicio", "fecha_fin", "activo")
    search_fields = ("nombre",)
    list_filter = ("activo",)


@admin.register(Curso)
class CursoAdmin(BaseAdmin):
    list_display = ("codigo", "nombre", "carrera", "semestre", "creditos")
    search_fields = ("codigo", "nombre")
    list_filter = ("carrera", "semestre")


# ---------------------------------------------------------------------
# 3. PERSONAS
# ---------------------------------------------------------------------
@admin.register(Profesor)
class ProfesorAdmin(BaseAdmin):
    list_display = ("cedula", "apellidos", "nombres", "email", "titulo")
    search_fields = ("cedula", "apellidos", "nombres", "email")


@admin.register(Estudiante)
class EstudianteAdmin(BaseAdmin):
    list_display = ("cedula", "apellidos", "nombres", "carrera", "email")
    search_fields = ("cedula", "apellidos", "nombres", "email")
    list_filter = ("carrera",)


# ---------------------------------------------------------------------
# 4. OFERTA
# ---------------------------------------------------------------------
@admin.register(Seccion)
class SeccionAdmin(BaseAdmin):
    # "inscritos" es una propiedad del modelo: el admin también la puede mostrar como columna
    list_display = ("curso", "paralelo", "jornada", "periodo", "profesor", "cupo", "inscritos")
    search_fields = ("curso__codigo", "curso__nombre", "profesor__apellidos")
    list_filter = ("periodo", "jornada", "curso__carrera")


# ---------------------------------------------------------------------
# 5. PROCESO
# ---------------------------------------------------------------------
class NotaInline(admin.StackedInline):
    """La Nota se edita DENTRO del formulario de la Matrícula."""
    model = Nota
    max_num = 1          # 1:1 → como máximo una nota por matrícula
    extra = 1            # muestra el formulario vacío si todavía no tiene nota
    # promedio y estado son editable=False: se muestran en solo lectura (los calcula save())
    readonly_fields = ("promedio", "estado") + CAMPOS_AUDITORIA


@admin.register(Matricula)
class MatriculaAdmin(BaseAdmin):
    list_display = ("estudiante", "seccion", "fecha")
    search_fields = ("estudiante__cedula", "estudiante__apellidos", "estudiante__nombres")
    list_filter = ("seccion__periodo", "seccion__jornada", "seccion__curso")
    date_hierarchy = "fecha"      # navegación por fechas encima del listado
    inlines = [NotaInline]


@admin.register(Nota)
class NotaAdmin(BaseAdmin):
    list_display = ("matricula", "n1", "n2", "n3", "promedio", "estado")
    search_fields = ("matricula__estudiante__apellidos", "matricula__estudiante__cedula")
    list_filter = ("estado", "matricula__seccion__periodo", "matricula__seccion__jornada")
    readonly_fields = ("promedio", "estado") + CAMPOS_AUDITORIA
