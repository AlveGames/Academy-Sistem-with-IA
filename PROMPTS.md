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
