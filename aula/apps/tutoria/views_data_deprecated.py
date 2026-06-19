# This Python file uses the following encoding: utf-8


# templates

# workflow

# auth
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min, Q

from aula.apps.alumnes.models import Alumne, Grup

# exceptions
from aula.apps.horaris.models import FranjaHoraria, Horari
from aula.apps.presencia.models import ControlAssistencia
from aula.apps.usuaris.models import User2Professor

# forms
# helpers
from aula.utils import tools
from aula.utils.decorators import group_required
from aula.utils.tools import llista, unicode


@login_required
@group_required(["professors"])
def justificadorMKTable(request, year, month, day):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials
    professor = User2Professor(user)

    data = date(year=int(year), month=int(month), day=int(day))
    grups = Grup.objects.filter(tutor__professor=professor)

    q_grups_tutorats = Q(grup__in=[t.grup for t in professor.tutor_set.all()])
    q_alumnes_tutorats = Q(
        pk__in=[ti.alumne.pk for ti in professor.tutorindividualitzat_set.all()]
    )
    alumnes = Alumne.objects.filter(q_grups_tutorats | q_alumnes_tutorats)

    # busco el dilluns i el divendres
    dia_de_la_setmana = data.weekday()

    delta = timedelta(days=(-1 * dia_de_la_setmana))
    dilluns = data + delta

    # marc horari per cada dia
    dades = tools.classebuida()
    dades.alumnes = alumnes.order_by("grup", "cognoms", "nom")
    dades.c = []  # controls

    dades.dia_hores = tools.diccionari()
    dades.marc_horari = {}
    for delta in [0, 1, 2, 3, 4]:
        dia = dilluns + timedelta(days=delta)
        Q(grup__in=grups)
        Q(grup__alumne__in=alumnes)
        q_impartir = Q(impartir__controlassistencia__alumne__in=alumnes)
        q_dies = Q(impartir__dia_impartir=dia)

        # forquilla = Horari.objects.filter( ( q_grups | q_alumnes ) & q_dies
        forquilla = Horari.objects.filter(q_impartir & q_dies).aggregate(
            desde=Min("hora__hora_inici"), finsa=Max("hora__hora_inici")
        )
        if forquilla["desde"] and forquilla["finsa"]:
            dades.marc_horari[dia] = {
                "desde": forquilla["desde"],
                "finsa": forquilla["finsa"],
            }
            dades.dia_hores[dia] = llista()
            for hora in FranjaHoraria.objects.filter(
                hora_inici__gte=forquilla["desde"], hora_inici__lte=forquilla["finsa"]
            ).order_by("hora_inici"):
                dades.dia_hores[dia].append(hora)

    dades.quadre = tools.diccionari()

    for alumne in dades.alumnes:
        dades.quadre[unicode(alumne)] = []

        for dia, hores in dades.dia_hores.itemsEnOrdre():
            hora_inici = FranjaHoraria.objects.get(
                hora_inici=dades.marc_horari[dia]["desde"]
            )
            hora_fi = FranjaHoraria.objects.get(
                hora_inici=dades.marc_horari[dia]["finsa"]
            )

            q_controls = (
                Q(impartir__dia_impartir=dia)
                & Q(impartir__horari__hora__gte=hora_inici)
                & Q(impartir__horari__hora__lte=hora_fi)
                & Q(alumne=alumne)
            )

            controls = [
                c
                for c in ControlAssistencia.objects.select_related(
                    "estat",
                    "impartir__horari__assignatura",
                    "professor",
                    "estat_backup",
                    "professor_backup",
                ).filter(q_controls)
            ]

            for hora in hores:
                cella = tools.classebuida()
                cella.txt = ""
                hiHaControls = (
                    len([c for c in controls if c.impartir.horari.hora == hora]) > 0
                )
                haPassatLlista = (
                    hiHaControls
                    and len(
                        [
                            c
                            for c in controls
                            if c.estat is not None and c.impartir.horari.hora == hora
                        ]
                    )
                    > 0
                )

                cella.c = [c for c in controls if c.impartir.horari.hora == hora]
                for item in cella.c:
                    item.professor2show = item.professor or (
                        item.impartir.horari.professor if item.impartir.horari else " "
                    )
                    item.estat2show = item.estat or " "
                dades.c.extend(cella.c)

                if not hiHaControls:
                    cella.color = "#505050"
                else:
                    if not haPassatLlista:
                        cella.color = "#E0E0E0"
                    else:
                        cella.color = "white"

                if hora == hora_inici:
                    cella.primera_hora = True
                else:
                    cella.primera_hora = False

                dades.quadre[unicode(alumne)].append(cella)

    return dades
