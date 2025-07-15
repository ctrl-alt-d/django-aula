# This Python file uses the following encoding: utf-8
from django.template.defaultfilters import date

from aula.apps.tutoria.models import CartaAbsentisme
from aula.utils import tools


def totesLesCartesRpt():
    report = []

    # --- Grups ----------------------------------------------------------------------------

    taula = tools.classebuida()

    taula.titol = tools.classebuida()
    taula.titol.contingut = ""
    taula.titol.enllac = None

    taula.capceleres = []

    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = "Data"
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 60
    capcelera.contingut = "Alumne"
    capcelera.enllac = ""
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = "Cartes nº."
    taula.capceleres.append(capcelera)

    taula.fileres = []

    for carta in CartaAbsentisme.objects.all().order_by("-data_carta"):
        filera = []

        # -data--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = date(carta.data_carta, "j N Y")
        filera.append(camp)

        # -alumne--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None

        from aula.apps.alumnes.named_instances import curs_any_fi

        te_mes_de_16 = (
            ", Més de 16 anys (durant el curs)"
            if (
                carta.alumne.cursa_obligatoria()
                and (curs_any_fi() - carta.alumne.data_neixement.year) > 16
            )
            else ""
        )
        camp.contingut = "{0} - {1} {2}".format(
            carta.alumne, carta.alumne.grup, te_mes_de_16
        )
        filera.append(camp)

        # -carta num--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = r"/tutoria/imprimirCartaNoFlag/{0}".format(carta.pk)
        camp.contingut = "{0}".format(carta.carta_numero)
        filera.append(camp)

        # --
        taula.fileres.append(filera)

    report.append(taula)

    return report
