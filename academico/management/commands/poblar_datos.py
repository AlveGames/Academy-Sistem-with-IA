# =====================================================================
# academico/management/commands/poblar_datos.py
# Se ejecuta con:  python manage.py poblar_datos
# Crea datos de prueba. Si ya existen, NO los duplica (get_or_create).
# =====================================================================
from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from academico.models import (
    Carrera, Curso, Estudiante, Facultad, Jornada, Matricula, Nota,
    Periodo, Profesor, Seccion, Semestre, Universidad,
)


class Command(BaseCommand):
    help = "Crea datos de prueba del sistema académico (sin duplicar)"

    @transaction.atomic   # todo o nada: si algo falla a la mitad, no queda nada a medias
    def handle(self, *args, **options):
        # Si ya existe un superusuario, lo ponemos como "Registrado por" (si no, queda vacío)
        admin = User.objects.filter(is_superuser=True).first()

        # get_or_create(campos_para_buscar, defaults={campos_solo_al_crear})
        # devuelve (objeto, creado) → creado es True si lo acaba de crear
        # Aquí usamos [0] porque solo nos interesa el objeto.

        # ---------------- 1. ESTRUCTURA ----------------
        ug = Universidad.objects.get_or_create(
            nombre="Universidad de Guayaquil",
            defaults={"siglas": "UG", "ciudad": "Guayaquil", "user": admin})[0]
        espol = Universidad.objects.get_or_create(
            nombre="Escuela Superior Politécnica del Litoral",
            defaults={"siglas": "ESPOL", "ciudad": "Guayaquil", "user": admin})[0]

        mate = Facultad.objects.get_or_create(
            universidad=ug, nombre="Ciencias Matemáticas y Físicas",
            defaults={"decano": "Ing. Jorge Salazar", "user": admin})[0]
        industrial = Facultad.objects.get_or_create(
            universidad=ug, nombre="Ingeniería Industrial",
            defaults={"decano": "Ing. Rosa Andrade", "user": admin})[0]
        Facultad.objects.get_or_create(   # no la guardamos en variable: no tiene carreras de prueba
            universidad=espol, nombre="Ingeniería en Electricidad y Computación",
            defaults={"decano": "PhD. Luis Cedeño", "user": admin})

        sof = Carrera.objects.get_or_create(
            codigo="SOF", defaults={"facultad": mate, "nombre": "Software", "user": admin})[0]
        red = Carrera.objects.get_or_create(
            codigo="RED", defaults={"facultad": mate, "nombre": "Redes y Telecomunicaciones", "user": admin})[0]
        ind = Carrera.objects.get_or_create(
            codigo="IND", defaults={"facultad": industrial, "nombre": "Ingeniería Industrial",
                                    "duracion_semestres": 10, "user": admin})[0]

        # ---------------- 2. CATÁLOGO ----------------
        s1 = Semestre.objects.get_or_create(numero=1, defaults={"nombre": "Primer semestre", "user": admin})[0]
        s2 = Semestre.objects.get_or_create(numero=2, defaults={"nombre": "Segundo semestre", "user": admin})[0]

        periodo = Periodo.objects.get_or_create(
            nombre="2026-1",
            defaults={"fecha_inicio": date(2026, 4, 1), "fecha_fin": date(2026, 8, 31),
                      "activo": True, "user": admin})[0]

        # (codigo, nombre, carrera, semestre, creditos)
        datos_cursos = [
            ("SOF-101", "Programación I", sof, s1, 4),
            ("SOF-102", "Matemática Discreta", sof, s1, 3),
            ("SOF-201", "Programación II", sof, s2, 4),
            ("RED-101", "Fundamentos de Redes", red, s1, 4),
            ("RED-201", "Enrutamiento", red, s2, 4),
            ("IND-101", "Dibujo Técnico", ind, s1, 3),
        ]
        cursos = {}   # diccionario codigo → curso, para usarlos después
        for codigo, nombre, carrera, semestre, creditos in datos_cursos:
            cursos[codigo] = Curso.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "carrera": carrera, "semestre": semestre,
                          "creditos": creditos, "user": admin})[0]

        # ---------------- 3. PERSONAS ----------------
        # (cedula, nombres, apellidos, titulo)
        datos_profesores = [
            ("0911111111", "Carlos", "Vera", "Mg. en Software"),
            ("0922222222", "María", "León", "Mg. en Ciencias de la Computación"),
            ("0933333333", "Pedro", "Castro", "Mg. en Telecomunicaciones"),
        ]
        profesores = []
        for cedula, nombres, apellidos, titulo in datos_profesores:
            profesores.append(Profesor.objects.get_or_create(
                cedula=cedula,
                defaults={"nombres": nombres, "apellidos": apellidos, "titulo": titulo,
                          "email": f"{nombres.lower()}.{apellidos.lower()}@ug.edu.ec", "user": admin})[0])
        vera, leon, castro = profesores   # "desempaquetar" la lista en 3 variables

        # (cedula, nombres, apellidos, carrera): 10 de Software y 5 de Redes
        datos_estudiantes = [
            ("0912345678", "Ana", "Pérez", sof),
            ("0999999999", "Luis", "Mora", sof),
            ("0988888888", "Eva", "Ruiz", sof),
            ("0911223344", "Diego", "Torres", sof),
            ("0922334455", "Camila", "Zambrano", sof),
            ("0933445566", "Andrés", "Bravo", sof),
            ("0944556677", "Valeria", "Molina", sof),
            ("0955667788", "José", "Villacís", sof),
            ("0966778899", "Daniela", "Ortiz", sof),
            ("0977889900", "Mateo", "Suárez", sof),
            ("0910203040", "Sofía", "Cevallos", red),
            ("0920304050", "Kevin", "Alvarado", red),
            ("0930405060", "Paula", "Macías", red),
            ("0940506070", "Bryan", "Chávez", red),
            ("0950607080", "Gabriela", "Mendoza", red),
        ]
        estudiantes = []
        for i, (cedula, nombres, apellidos, carrera) in enumerate(datos_estudiantes):
            estudiantes.append(Estudiante.objects.get_or_create(
                cedula=cedula,
                defaults={"nombres": nombres, "apellidos": apellidos, "carrera": carrera,
                          "email": f"{nombres.lower()}.{apellidos.lower()}@estudiante.ug.edu.ec",
                          "telefono": f"09{8000000 + i * 1111:08d}",
                          "fecha_nacimiento": date(2004 + i % 4, 1 + i % 12, 1 + i), "user": admin})[0])
        est_sof = estudiantes[:10]   # los 10 primeros (slicing)
        est_red = estudiantes[10:]   # los 5 últimos

        # ---------------- 4. OFERTA: 4 secciones (diurnas y nocturnas) ----------------
        def seccion(curso, profesor, paralelo, jornada, cupo):
            # buscamos por la restricción única (curso, periodo, paralelo, jornada)
            return Seccion.objects.get_or_create(
                curso=curso, periodo=periodo, paralelo=paralelo, jornada=jornada,
                defaults={"profesor": profesor, "cupo": cupo, "user": admin})[0]

        sof101_a = seccion(cursos["SOF-101"], vera, "A", Jornada.DIURNA, 30)
        sof101_b = seccion(cursos["SOF-101"], leon, "B", Jornada.NOCTURNA, 25)
        sof102_a = seccion(cursos["SOF-102"], vera, "A", Jornada.DIURNA, 30)
        red101_a = seccion(cursos["RED-101"], castro, "A", Jornada.NOCTURNA, 20)

        # ---------------- 5. PROCESO: 25 matrículas con sus notas ----------------
        # Cada estudiante solo se matricula en cursos de SU carrera (regla de Matricula.clean()):
        #   10 de Software → SOF-101 (5 en A diurna, 5 en B nocturna) + SOF-102 A  = 20
        #   5 de Redes     → RED-101 A nocturna                                    =  5
        parejas = []
        for i, est in enumerate(est_sof):
            parejas.append((est, sof101_a if i < 5 else sof101_b))
            parejas.append((est, sof102_a))
        for est in est_red:
            parejas.append((est, red101_a))

        # Notas (n1, n2, n3) variadas: se repiten en ciclo. Unas aprueban y otras no.
        notas_ejemplo = [
            (80, 65, 66),    # 70.33 aprobado (justo)
            (90, 85, 88),    # 87.67 aprobado
            (60, 70, 55),    # 61.67 reprobado
            (95, 92, 98),    # 95.00 aprobado
            (45, 50, 60),    # 51.67 reprobado
            (70, 70, 69),    # 69.67 reprobado (¡por poco!)
            (75, 80, 72),    # 75.67 aprobado
        ]

        for i, (est, sec) in enumerate(parejas):
            matricula = Matricula.objects.get_or_create(
                estudiante=est, seccion=sec,
                defaults={"fecha": date(2026, 3, 20 + i % 5), "user": admin})[0]
            n1, n2, n3 = notas_ejemplo[i % len(notas_ejemplo)]
            # get_or_create llama a save() al crear → Nota.save() calcula promedio y estado
            Nota.objects.get_or_create(
                matricula=matricula,
                defaults={"n1": Decimal(n1), "n2": Decimal(n2), "n3": Decimal(n3), "user": admin})

        # ---------------- Resumen ----------------
        for modelo in (Universidad, Facultad, Carrera, Semestre, Periodo, Curso,
                       Profesor, Estudiante, Seccion, Matricula, Nota):
            self.stdout.write(f"  {modelo._meta.verbose_name_plural}: {modelo.objects.count()}")
        aprobados = Nota.objects.filter(estado="aprobado").count()
        self.stdout.write(f"  Notas aprobadas: {aprobados} · reprobadas: {Nota.objects.count() - aprobados}")
        self.stdout.write(self.style.SUCCESS("Datos de prueba listos"))
