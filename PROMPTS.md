# Bitácora de prompts · Sistema Académico con IA

## 1. Proyecto inicial (2026-11-25)

**Prompt (resumen):** Prompt 0 con el contexto y las reglas del proyecto + tarea: crear el venv,
instalar django, pillow, openpyxl y xhtml2pdf, generar requirements.txt, crear el proyecto
`sistema_academico` (con el punto) y las apps `core` y `academico`, agregarlas a INSTALLED_APPS,
crear .gitignore y PROMPTS.md, y hacer `git init` con el commit "Proyecto inicial".

**Qué se hizo:**
- `python -m venv venv` e instalación de las 4 librerías.
- `pip freeze > requirements.txt`.
- `django-admin startproject sistema_academico .` y `python manage.py startapp core` / `academico`.
- `core` y `academico` agregadas a INSTALLED_APPS en `sistema_academico/settings.py`.
- `.gitignore` con venv/, `__pycache__/` y `*.pyc` (media/ NO se ignora).
- `python manage.py check` → sin problemas.

**Errores y cómo se corrigieron:**
- La guía pide Python 3.12, pero en la PC solo está instalado Python 3.13. Se usó 3.13,
  que es compatible con Django (se instaló Django 6.1.3).
- Al principio la guía HTML no estaba en la carpeta; se copió y se leyó antes de empezar.

## 2. Prompt 1 · Crear los modelos (2026-11-25)

**Prompt (resumen):** crear `core/models.py` (ModeloBase abstracto con user, fecha_creacion y
fecha_modificacion) y `academico/models.py` con los 11 modelos, los choices Jornada y EstadoNota,
las restricciones únicas, `Periodo.clean()`, `Matricula.clean()` (carrera y cupo) y `Nota.save()`
(promedio y estado). Entregar además la tabla de relaciones.

**Qué se hizo:**
- Los dos archivos, con los mismos nombres de campos y related_name que el código de referencia de la guía (2.4).
- `makemigrations` (crea `academico/migrations/0001_initial.py`) y `migrate`: sin errores.
- Prueba en el shell con los datos de la guía (en una transacción que se deshizo al final):
  nota 80/65/66 → 70.33 Aprobado; con n2=40 → 62.00 Reprobado; matrícula de otra carrera y
  sección sin cupo → error de `clean()`; periodo con fechas al revés → error en fecha_fin.
- Diferencia con la referencia: se agregó `ordering` a Nota (por el apellido del estudiante),
  porque el prompt pide ordering en todos los modelos.

**Errores y cómo se corrigieron:**
- `ZoneInfoNotFoundError: 'No time zone found with key Guayaquil'`: en settings.py estaba
  `TIME_ZONE = 'Guayaquil'`. El nombre correcto es `'America/Guayaquil'`. (`check` no lo detecta en Windows.)
- Al imprimir "→" en la consola de Windows salió `UnicodeEncodeError`; se resolvió con `PYTHONIOENCODING=utf-8`
  (solo afecta la prueba, no el proyecto).

## 3. Prompt 2 · Admin y datos de prueba (2026-11-25)

**Prompt (resumen):** en `academico/admin.py`, una clase BaseAdmin (auditoría en solo lectura y
`obj.user = request.user` en `save_model()`) y los 11 modelos registrados con list_display,
search_fields y list_filter, más la Nota como inline de la Matrícula. Además, el comando
`poblar_datos` con datos de prueba que no se dupliquen (get_or_create).

**Qué se hizo:**
- `academico/admin.py`: BaseAdmin con `readonly_fields` y `save_model()`. También tiene `save_formset()`,
  para que la Nota guardada desde el inline lleve el usuario. Los 11 admin heredan de BaseAdmin
  (Seccion se filtra por periodo, jornada y carrera). NotaInline es un StackedInline con max_num=1
  y muestra promedio/estado en solo lectura.
- `academico/management/__init__.py`, `commands/__init__.py` y `commands/poblar_datos.py`:
  2 universidades, 3 facultades, 3 carreras, 2 semestres, 1 periodo activo, 6 cursos, 3 profesores,
  4 secciones (2 diurnas y 2 nocturnas), 15 estudiantes, 25 matrículas y 25 notas (15 aprobadas, 10 reprobadas).
  Cada estudiante solo se matricula en cursos de su carrera, para cumplir `Matricula.clean()`.
- Pruebas: el comando se ejecutó dos veces y no duplicó nada; las 25 matrículas pasan `full_clean()`;
  todas las páginas del admin responden 200; cambiar n2 a 40 en el inline pasa la nota a Reprobado;
  matricular a un estudiante de Redes en SOF-102 muestra el error de `clean()`.

**Errores y cómo se corrigieron:**
- La zona horaria seguía como `TIME_ZONE = 'Guayaquil'` en settings.py (ya estaba en el commit anterior).
  Se corrigió a `'America/Guayaquil'`, porque con ese valor el comando y el admin se caían.
- En la prueba automática del admin salió `DisallowedHost: 'testserver'`: el cliente de pruebas usa ese host.
  Se probó con `Client(HTTP_HOST='localhost')`. No se cambió ALLOWED_HOSTS.
