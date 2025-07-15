# This Python file uses the following encoding: utf-8

import os

from django.conf import settings

from aula.utils.tools import unicode


def report_cartaAbsentisme(request, carta):
    # from django.template import Context
    import html
    import time

    from appy.pod.renderer import Renderer
    from django import http

    excepcio = None
    contingut = None
    try:
        # resultat = StringIO.StringIO( )
        resultat = "/tmp/DjangoAula-temp-{0}-{1}.odt".format(
            time.time(), request.session.session_key
        )
        # context = Context( {'reports' : reports, } )
        path = None
        path = os.path.join(
            settings.PROJECT_DIR, "../customising/docs/cartesFaltesAssistencia.odt"
        )
        if not os.path.isfile(path):
            path = os.path.join(
                os.path.dirname(__file__), "templates/cartesFaltesAssistencia.odt"
            )

        # amorilla@xtec.cat
        try:
            datafmt = settings.CUSTOM_DATE_FORMAT
            carta_data = carta.data_carta.strftime(datafmt) if carta.data_carta else ""
        except:  # noqa: E722
            datafmt = "%-d %B de %Y"
            carta_data = carta.data_carta.strftime(datafmt) if carta.data_carta else ""

        try:
            des_de_data = carta.faltes_des_de_data.strftime("%d/%m/%Y")
        except:  # noqa: E722
            des_de_data = ""

        dades_report = {
            "professor": carta.professor,
            "alumne": unicode(carta.alumne),
            "grup": unicode(carta.alumne.grup),
            "nfaltes": carta.nfaltes,
            "year": carta.data_carta.year if carta.data_carta else "",
            "fins_a_data": (
                carta.faltes_fins_a_data.strftime("%d/%m/%Y")
                if carta.faltes_fins_a_data
                else ""
            ),
            "tipus1": carta.tipus_carta == "tipus1",
            "tipus2": carta.tipus_carta == "tipus2",
            "tipus3A": carta.tipus_carta == "tipus3A",
            "tipus3B": carta.tipus_carta == "tipus3B",
            "tipus3C": carta.tipus_carta == "tipus3C",
            "tipus3D": carta.tipus_carta == "tipus3D",
            # amorilla@xtec.cat
            # nous elements per personalitzar la carta
            "data": carta_data,
            "des_de_data": des_de_data,
            "adreca": carta.alumne.adreca,
            "cp": carta.alumne.cp,
            "localitat": carta.alumne.localitat,
            "municipi": carta.alumne.municipi,
            "cognoms": carta.alumne.cognoms,
            "nivell": carta.alumne.getNivellCustom(),  # nivell de CUSTOM_NIVELLS
            "edat": carta.alumne.edat(carta.data_carta) if carta.data_carta else "",
            "numcarta": carta.carta_numero,
        }

        renderer = Renderer(path, dades_report, resultat)
        renderer.run()
        docFile = open(resultat, "rb")
        contingut = docFile.read()
        docFile.close()
        os.remove(resultat)

    except Exception as e:
        excepcio = unicode(e)

    if not excepcio:
        response = http.HttpResponse(
            contingut, content_type="application/vnd.oasis.opendocument.text"
        )
        response["Content-Disposition"] = "attachment; filename=cartaAbsencies.odt"
    else:
        response = http.HttpResponse(
            """Gremlin's ate you! %s""" % html.escape(excepcio)
        )

    return response
