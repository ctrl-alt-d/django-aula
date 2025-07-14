# This Python file uses the following encoding: utf-8
from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q

from aula.apps.alumnes.models import Alumne
from aula.apps.tutoria.models import CartaAbsentisme, Tutor
from aula.utils import tools
from aula.utils.tools import unicode


def gestioCartesRpt(professor, l4):
    report = []

    dataDesDe = None
    dataFinsA = date.today()

    # --- taula de pendents d'imprimir --
    taula = tools.classebuida()

    taula.titol = tools.classebuida()
    taula.titol.contingut = ""
    taula.titol.enllac = None

    taula.capceleres = []

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = "Cartes pendents d'imprimir"
    capcelera.enllac = ""
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 30
    capcelera.contingut = ""
    capcelera.enllac = ""
    taula.capceleres.append(capcelera)

    taula.fileres = []

    for carta in CartaAbsentisme.objects.filter(professor=professor, impresa=False):
        filera = []

        # -carta--------------------------------------------
        camp = tools.classebuida()
        camp.codi = carta.pk
        camp.enllac = None
        camp.contingut = unicode(carta)
        filera.append(camp)

        camp = tools.classebuida()
        camp.codi = carta.pk
        camp.enllac = None
        camp.multipleContingut = (
            ("Imprimir", r"/tutoria/imprimirCarta/{0}".format(carta.pk)),
        )
        camp.esMenu = True
        filera.append(camp)

        taula.fileres.append(filera)

    if bool(taula.fileres):
        report.append(taula)

    # --- Grups ----------------------------------------------------------------------------
    grups = [t.grup for t in Tutor.objects.filter(professor=professor)]
    grups.append("Altres")

    for grup in grups:
        taula = tools.classebuida()

        taula.titol = tools.classebuida()
        taula.titol.contingut = ""
        taula.titol.enllac = None

        taula.capceleres = []

        capcelera = tools.classebuida()
        capcelera.amplade = 30
        capcelera.contingut = (
            grup if grup == "Altres" else "{0} ({1})".format(grup, grup.curs)
        )
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 10
        capcelera.contingut = "Faltes."
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 10
        capcelera.contingut = "Cartes."
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 30
        capcelera.contingut = "Faltes acumulades per a nova carta\n(Recordar 3 darrers dies no entra al còmput)."
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = "Accions"
        taula.capceleres.append(capcelera)

        taula.fileres = []

        if grup == "Altres":
            consulta_alumnes = Q(
                pk__in=[ti.alumne.pk for ti in professor.tutorindividualitzat_set.all()]
            )
        else:
            consulta_alumnes = Q(grup=grup)

        for alumne in Alumne.objects.filter(consulta_alumnes, data_baixa__isnull=True):
            filera = []

            # -moment--------------------------------------------
            camp = tools.classebuida()
            camp.codi = alumne.pk
            camp.enllac = None
            camp.contingut = unicode(alumne)
            camp.enllac = "/tutoria/detallTutoriaAlumne/{0}/dades".format(alumne.pk)
            filera.append(camp)

            q_hores = Q(impartir__dia_impartir__lte=dataFinsA)
            if dataDesDe:
                q_hores &= Q(impartir__dia_impartir__gte=dataDesDe)

            controls = alumne.controlassistencia_set.filter(q_hores)

            # -faltes--------------------------------------------
            f = controls.filter(alumne=alumne, estat__codi_estat="F").distinct().count()
            r = controls.filter(alumne=alumne, estat__codi_estat="R").distinct().count()
            if settings.CUSTOM_NO_CONTROL_ES_PRESENCIA:
                p = (
                    controls.filter(alumne=alumne)
                    .filter(
                        Q(estat__codi_estat__in=["P", "O"])
                        | Q(estat__codi_estat__isnull=True)
                    )
                    .distinct()
                    .count()
                )
            else:
                p = (
                    controls.filter(alumne=alumne, estat__codi_estat__in=["P", "O"])
                    .distinct()
                    .count()
                )
            j = controls.filter(alumne=alumne, estat__codi_estat="J").distinct().count()
            # ca = controls.filter(q_hores).filter(estat__codi_estat__isnull = False).filter( alumne = alumne ).distinct().count()

            # -%--------------------------------------------
            tpc = (1.0 * f) * 100.0 / (0.0 + f + r + p + j) if f > 0 else 0

            camp = tools.classebuida()
            camp.enllac = None
            accio_list = [
                (
                    "f: {0}".format(f),
                    (
                        "/tutoria/detallTutoriaAlumne/{0}/assistencia".format(alumne.pk)
                        if f
                        else None
                    ),
                ),
                (
                    "j: {0}".format(j),
                    (
                        "/tutoria/detallTutoriaAlumne/{0}/assistencia".format(alumne.pk)
                        if j
                        else None
                    ),
                ),
                (
                    "r: {0}".format(r),
                    (
                        "/tutoria/detallTutoriaAlumne/{0}/assistencia".format(alumne.pk)
                        if r
                        else None
                    ),
                ),
                ("p: {0}".format(p), None),
                (
                    "{0:.2f}%noJust".format(tpc),
                    (
                        "/tutoria/detallTutoriaAlumne/{0}/assistencia".format(alumne.pk)
                        if f or j or r
                        else None
                    ),
                ),
            ]
            camp.multipleContingut = accio_list
            filera.append(camp)

            # -Cartes---------------
            camp = tools.classebuida()

            camp.multipleContingut = [
                (
                    "{0}".format(carta.data_carta),
                    "/tutoria/imprimirCarta/{0}".format(carta.pk),
                )
                for carta in alumne.cartaabsentisme_set.exclude(
                    carta_esborrada_moment__isnull=False
                ).all()
            ]

            if not bool(camp.multipleContingut):
                camp.contingut = "--"

            filera.append(camp)

            # -Faltes x a carta---------------
            camp = tools.classebuida()
            camp.enllac = None
            carta = CartaAbsentisme(alumne=alumne)

            msg = None
            cal_imprimir_carta = False

            try:
                carta.clean()
                llindar = settings.CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA.get(
                    carta.tipus_carta, settings.CUSTOM_FALTES_ABSENCIA_PER_CARTA
                )
                cal_imprimir_carta = carta.nfaltes >= llindar
            except ValidationError as e:
                msg = ". ".join([str(v) for v in e.messages])

            camp.contingut = msg if bool(msg) else carta.nfaltes

            filera.append(camp)

            # -Accions---------------
            camp = tools.classebuida()

            camp.enllac = None
            camp.multipleContingut = (
                [
                    ("Generar Nova Carta", "/tutoria/novaCarta/{0}".format(alumne.pk)),
                ]
                if cal_imprimir_carta
                else []
            )

            darrera_carta = None
            try:
                darrera_carta = alumne.cartaabsentisme_set.exclude(
                    carta_esborrada_moment__isnull=False
                ).order_by("-data_carta")[0]
            except IndexError:
                pass

            if l4 and darrera_carta:
                camp.multipleContingut.append(
                    (
                        "Esborrar carta {0}".format(darrera_carta.data_carta),
                        "/tutoria/esborraCarta/{0}".format(darrera_carta.pk),
                    )
                )

            camp.esMenu = True

            filera.append(camp)

            # --
            taula.fileres.append(filera)
        report.append(taula)

    return report
