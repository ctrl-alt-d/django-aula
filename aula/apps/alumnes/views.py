# This Python file uses the following encoding: utf-8

# templates
from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib import messages

# auth
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms.models import modelform_factory, modelformset_factory

# workflow
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse
from django_tables2 import RequestConfig

# forms
from aula.apps.alumnes.forms import (
    newAlumne,
    promoForm,
    triaAlumneForm,
    triaAlumneSelect2Form,
    triaMultiplesAlumnesForm,
)
from aula.apps.alumnes.gestioGrups import grupsPromocionar

# from django import forms as forms
from aula.apps.alumnes.models import Alumne, Curs, DadesAddicionalsAlumne, Grup
from aula.apps.alumnes.reports import reportLlistaTutorsIndividualitzats
from aula.apps.alumnes.rpt_duplicats import duplicats_rpt

# tables
from aula.apps.alumnes.tables2_models import AlumneNomSentitTable, HorariAlumneTable
from aula.apps.alumnes.tools import fusiona_alumnes_by_pk
from aula.apps.missatgeria.missatges_a_usuaris import (
    ALUMNES_ASSIGNAR_NOMSENTIT,
    ALUMNES_ESBORRAR_NOMSENTIT,
    tipusMissatge,
)

# missatgeria
from aula.apps.missatgeria.models import Missatge
from aula.apps.presencia.models import Impartir
from aula.apps.tutoria.models import TutorIndividualitzat
from aula.apps.usuaris.models import Accio, Professor, User2Professor

# helpers
from aula.utils import tools
from aula.utils.decorators import group_required
from aula.utils.tools import unicode

# duplicats
from ...settings import CUSTOM_DADES_ADDICIONALS_ALUMNE


@login_required
@group_required(["direcció"])
def duplicats(request):
    report = duplicats_rpt()

    return render(
        request,
        "report.html",
        {
            "report": report,
            "head": "Alumnes",
        },
    )


# duplicats
@login_required
@group_required(["direcció"])
def fusiona(request, pk):
    credentials = tools.getImpersonateUser(request)
    resultat = {
        "errors": [],
        "warnings": [],
        "infos": ["Procés realitzat correctament"],
    }
    try:
        fusiona_alumnes_by_pk(int(pk), credentials)
    except Exception as e:
        resultat = {
            "errors": [
                unicode(e),
            ],
            "warnings": [],
            "infos": [],
        }

    return render(
        request,
        "resultat.html",
        {"head": "Error a l'esborrar actuació.", "msgs": resultat},
    )


# vistes--------------------------------------------------------------------------------------


# vistes--------------------------------------------------------------------------------------


@login_required
@group_required(["direcció"])
def assignaTutors(request):
    # FormSet: Una opció seria fer servir formSet, però em sembla que
    # com ho estic fent ara és més fàcil per l'usuari
    # https://docs.djangoproject.com/en/dev/topics/forms/formsets
    from aula.apps.alumnes.forms import tutorsForm
    from aula.apps.tutoria.models import Tutor

    # prefixes:
    # https://docs.djangoproject.com/en/dev/ref/forms/api/#prefixes-for-forms
    formset = []
    if request.method == "POST":
        # un formulari per cada grup
        # totBe = True
        parellesProfessorGrup = list()
        for grup in (
            Grup.objects.filter(alumne__isnull=False)
            .distinct()
            .order_by("descripcio_grup")
        ):
            form = tutorsForm(request.POST, prefix=str(grup.pk))
            formset.append(form)
            if form.is_valid():
                tutor1 = form.cleaned_data["tutor1"]
                tutor2 = form.cleaned_data["tutor2"]
                tutor3 = form.cleaned_data["tutor3"]
                if tutor1:
                    parellesProfessorGrup.append((tutor1.pk, grup))
                if tutor2 and tutor2 != tutor1:
                    parellesProfessorGrup.append((tutor2.pk, grup))
                if tutor3 and tutor3 != tutor2 and tutor3 != tutor1:
                    parellesProfessorGrup.append((tutor3.pk, grup))
            else:
                pass
                # totBe = False

        Tutor.objects.all().delete()
        for tutor_pk, grup in parellesProfessorGrup:
            professor = Professor.objects.get(pk=tutor_pk)
            nouTutor = Tutor(professor=professor, grup=grup)
            nouTutor.save()
            # return HttpResponseRedirect( '/' )

    else:
        for grup in (
            Grup.objects.filter(alumne__isnull=False)
            .distinct()
            .order_by("descripcio_grup")
        ):
            tutor1 = tutor2 = tutor3 = None
            if len(grup.tutor_set.all()) > 0:
                tutor1 = grup.tutor_set.all()[0].professor
            if len(grup.tutor_set.all()) > 1:
                tutor2 = grup.tutor_set.all()[1].professor
            if len(grup.tutor_set.all()) > 2:
                tutor3 = grup.tutor_set.all()[2].professor
            form = tutorsForm(
                prefix=str(grup.pk),
                initial={
                    "grup": grup,
                    "tutor1": tutor1,
                    "tutor2": tutor2,
                    "tutor3": tutor3,
                },
            )
            formset.append(form)

    return render(
        request,
        "formsetgrid.html",
        {
            "formset": formset,
            "head": "Gestió de tutors",
        },
    )


@login_required
@group_required(["direcció"])
def llistaTutorsIndividualitzats(request):
    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    User2Professor(user)

    head = "Tutors Individualitzats"

    report = reportLlistaTutorsIndividualitzats()

    return render(
        request,
        "report.html",
        {
            "report": report,
            "head": head,
        },
    )


@login_required
@group_required(["direcció", "psicopedagog"])
def informePsicopedagoc(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    if request.method == "POST":
        formAlumne = triaAlumneSelect2Form(
            request.POST
        )  # todo: multiple=True (multiples alumnes de cop)
        if formAlumne.is_valid():
            alumne = formAlumne.cleaned_data["alumne"]
            return HttpResponseRedirect(
                r"/tutoria/detallTutoriaAlumne/{0}/all/".format(alumne.pk)
            )

    else:
        formAlumne = triaAlumneSelect2Form()

    return render(request, "form.html", {"form": formAlumne, "head": "Triar alumne"})


@login_required
@group_required(["direcció", "psicopedagog"])
def canviarNomSentitW0(request):
    alumnes = list(
        Alumne.objects.exclude(nom_sentit="")
        .values("id", "cognoms", "nom", "nom_sentit")
        .order_by("nom_sentit")
    )
    for a in alumnes:
        a["cognom_nom"] = a["cognoms"] + ", " + a["nom"]

    table = AlumneNomSentitTable(alumnes)
    table.order_by = "nom_sentit"

    RequestConfig(request).configure(table)

    return render(
        request,
        "table2.html",
        {
            "table": table,
            "urladd": reverse("psico__nomsentit__w1"),
            "txtadd": "Nou alumne amb nom sentit",
            "titol_formulari": "Alumnes amb Nom Sentit",
        },
    )


@login_required
@group_required(["direcció", "psicopedagog"])
def canviarNomSentitW1(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    if request.method == "POST":
        formAlumne = triaAlumneSelect2Form(request.POST)
        if formAlumne.is_valid():
            alumne = formAlumne.cleaned_data["alumne"]
            url_next = reverse(
                "psico__nomsentit__w2",
                kwargs={
                    "pk": alumne.pk,
                },
            )
            return HttpResponseRedirect(url_next)

    else:
        formAlumne = triaAlumneSelect2Form()

    return render(request, "form.html", {"form": formAlumne, "head": "Triar alumne"})


@login_required
@group_required(["direcció", "psicopedagog"])
def canviarNomSentitW2(request, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    alumne = get_object_or_404(Alumne, pk=pk)
    formF = modelform_factory(Alumne, fields=["nom_sentit"])
    if request.method == "POST":
        formAlumne = formF(request.POST, instance=alumne)
        if formAlumne.is_valid():
            formAlumne.save()

            # modificar o esborrar?
            esborrat = not alumne.nom_sentit

            # missatge a tutors i professors
            qElTenenALHorari = Q(horari__impartir__controlassistencia__alumne=alumne)
            qImparteixDocenciaAlNouGrup = Q(horari__grup=alumne.grup)
            qEsTutor = Q(pk__in=[p.pk for p in alumne.tutorsDeLAlumne()])
            professors = Professor.objects.filter(
                qElTenenALHorari | qImparteixDocenciaAlNouGrup | qEsTutor
            ).distinct()

            if esborrat:
                missatge = ALUMNES_ESBORRAR_NOMSENTIT
                tipus_de_missatge = tipusMissatge(missatge)
                missatge_txt = missatge.format(alumne)
            else:
                missatge = ALUMNES_ASSIGNAR_NOMSENTIT
                tipus_de_missatge = tipusMissatge(missatge)
                missatge_txt = missatge.format(
                    alumne,
                    alumne.nom_sentit,
                )

            for professor in professors:
                msg = Missatge(
                    remitent=user,
                    text_missatge=missatge_txt,
                    tipus_de_missatge=tipus_de_missatge,
                )
                msg.envia_a_usuari(professor, "IN")

            # missatge per pantalla
            professors_txt = ", ".join([unicode(professor) for professor in professors])
            msg = "El nom sentit de l'alumne {0} és: {1}. Els professors {2} han estat notificats.".format(
                alumne,
                alumne.nom_sentit,
                professors_txt,
            )
            if esborrat:
                msg = "Eliminat el nom sentit de l'alumne {0}. Els professors {1} han estat notificats.".format(
                    alumne, professors_txt
                )
            messages.success(request, msg)

            # fi
            url_next = reverse("psico__informes_alumne__list")
            return HttpResponseRedirect(url_next)

    else:
        formAlumne = formF(instance=alumne)

    return render(
        request,
        "form.html",
        {"form": formAlumne, "head": "Canviar el nom sentit a {0}".format(alumne)},
    )


@login_required
@group_required(["direcció"])
def gestionaAlumnesTutor(request, pk):
    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    professor = Professor.objects.get(pk=int(pk))

    head = "Tutors Individualitzats"
    formset = []

    if request.method == "POST":
        totBe = True
        nous_alumnes_tutor = []
        for grup in (
            Grup.objects.filter(alumne__isnull=False)
            .distinct()
            .order_by("descripcio_grup")
        ):
            # http://www.ibm.com/developerworks/opensource/library/os-django-models/index.html?S_TACT=105AGX44&S_CMP=EDU
            form = triaMultiplesAlumnesForm(
                request.POST,
                prefix=str(grup.pk),
                queryset=grup.alumne_set.all(),
                etiqueta=unicode(grup),
            )
            formset.append(form)
            if form.is_valid():
                for alumne in form.cleaned_data["alumnes"]:
                    nous_alumnes_tutor.append(alumne)
            else:
                totBe = False
        if totBe:
            professor.tutorindividualitzat_set.all().delete()
            for alumne in nous_alumnes_tutor:
                ti = TutorIndividualitzat(professor=professor, alumne=alumne)
                ti.credentials = credentials
                ti.save()

            return HttpResponseRedirect("/alumnes/llistaTutorsIndividualitzats/")
    else:
        for grup in (
            Grup.objects.filter(alumne__isnull=False)
            .distinct()
            .order_by("descripcio_grup")
        ):
            # http://www.ibm.com/developerworks/opensource/library/os-django-models/index.html?S_TACT=105AGX44&S_CMP=EDU
            inicial = [
                c.pk
                for c in grup.alumne_set.filter(
                    tutorindividualitzat__professor=professor
                )
            ]
            form = triaMultiplesAlumnesForm(
                prefix=str(grup.pk),
                queryset=grup.alumne_set.all(),
                etiqueta=unicode(grup),
                initial={"alumnes": inicial},
            )
            formset.append(form)

    return render(
        request,
        "formset.html",
        {
            "formset": formset,
            "head": head,
            "formSetDelimited": True,
        },
    )


# --------------------------------------------------------------------------------------------


@login_required
@group_required(["consergeria", "professors", "professional"])
def triaAlumne(request):
    if not request.user.is_authenticated:
        return render("/login")

    if request.method == "POST":
        form = triaAlumneForm(request.POST)
        if form.is_valid():
            return HttpResponse(unicode(form.cleaned_data["alumne"]))
    else:
        form = triaAlumneForm()

    return render(
        request,
        "form.html",
        {
            "form": form,
            "head": "Resultat importació SAGA",
        },
    )


# --------------------- AJAX per seleccionar un alumne --------------------------------------------#


@login_required
@group_required(["consergeria", "professors", "professional"])
def triaAlumneCursAjax(request, id_nivell):
    if request.method == "GET":  # request.is_ajax()
        id_nivell = int(id_nivell)
        cursos = Curs.objects.filter(nivell__pk=id_nivell)
        message = '<option value="" selected>-- Tria --</option>'
        for c in cursos:
            message += '<option value="%s">%s</option>' % (c.pk, unicode(c))
        return HttpResponse(message)


@login_required
@group_required(["consergeria", "professors", "professional"])
def triaAlumneGrupAjax(request, id_curs):
    if request.method == "GET":  # request.is_ajax()
        pk = int(id_curs)
        tots = Grup.objects.filter(curs__pk=pk)
        message = '<option value="" selected>-- Tria --</option>'
        for iterador in tots:
            message += '<option value="%s">%s</option>' % (
                iterador.pk,
                unicode(iterador),
            )
        return HttpResponse(message)


@login_required
@group_required(["consergeria", "professors", "professional"])
def triaAlumneAlumneAjax(request, id_grup):
    if request.method == "GET":  # request.is_ajax()
        pk = int(id_grup)
        tots = Alumne.objects.filter(grup__pk=pk)
        message = '<option value="" selected>-- Tria --</option>'
        for iterador in tots:
            message += '<option value="%s">%s</option>' % (
                iterador.pk,
                unicode(iterador),
            )
        return HttpResponse(message)


# ---------------------  --------------------------------------------#


@login_required
@group_required(["professors"])
def elsMeusAlumnesAndAssignatures(request):
    from django.db.models import Count, Max

    (user, l4) = tools.getImpersonateUser(request)
    professor = User2Professor(user)

    report = []

    nTaula = 0

    assignatura_grup = set()
    for ca in Impartir.objects.filter(horari__professor=professor):
        if ca.horari.grup is not None:
            assignatura_grup.add((ca.horari.assignatura, ca.horari.grup))

    for (
        assignatura,
        grup,
    ) in assignatura_grup:
        taula = tools.classebuida()
        taula.codi = nTaula
        nTaula += 1
        taula.tabTitle = "{0} - {1}".format(unicode(assignatura), unicode(grup))

        taula.titol = tools.classebuida()
        taula.titol.contingut = ""

        capcelera_foto = tools.classebuida()
        capcelera_foto.amplade = 5

        capcelera_nom = tools.classebuida()
        capcelera_nom.amplade = 25
        capcelera_nom.contingut = "{0} - {1}".format(
            unicode(assignatura), unicode(grup)
        )

        capcelera_nIncidencies = tools.classebuida()
        capcelera_nIncidencies.amplade = 5
        capcelera_nIncidencies.contingut = "Incidències"

        capcelera_assistencia = tools.classebuida()
        capcelera_assistencia.amplade = 5
        capcelera_assistencia.contingut = "Assist."

        capcelera_nFaltes = tools.classebuida()
        capcelera_nFaltes.amplade = 15

        # nClasses_grup és el total d'hores que el professor fa al grup.
        # Només té en compte hores amb alumnes.
        nClasses_grup = (
            Impartir.objects.filter(
                horari__professor=professor,
                horari__assignatura=assignatura,
                horari__grup=grup,
            )
            .exclude(
                controlassistencia__alumne__isnull=True,
            )
            .distinct()
            .count()
        )

        # nClassesImpartides_grup són les hores que ja ha impartit aquest professor al grup.
        # Només té en compte hores amb alumnes.
        nClassesImpartides_grup = (
            Impartir.objects.filter(
                horari__professor=professor,
                horari__assignatura=assignatura,
                horari__grup=grup,
                dia_impartir__lte=date.today(),
            )
            .exclude(
                controlassistencia__alumne__isnull=True,
            )
            .distinct()
            .count()
        )
        # Obté els alumnes escollits segons grup, assignatura i professor
        alumnes = (
            Alumne.objects.filter(
                controlassistencia__impartir__horari__grup=grup,
                controlassistencia__impartir__horari__assignatura=assignatura,
                controlassistencia__impartir__horari__professor=professor,
            )
            .distinct()
            .order_by("cognoms")
        )

        # nClasses_materia és el total d'hores que els alumnes fan d'aquesta matèria.
        # Varia en funció de l'alumne, es selecciona la màxima quantitat obtinguda per algun alumne.
        nClasses_materia = (
            Impartir.objects.filter(
                controlassistencia__alumne__in=alumnes, horari__assignatura=assignatura
            )
            .values("controlassistencia__alumne")
            .annotate(hores=Count("id", distinct=True))
            .aggregate(maxval=Max("hores"))
            .get("maxval", nClasses_grup)
        )

        # nClassesImpartides_materia són les hores que ja han impartit aquests alumnes en aquesta matèria.
        # Varia en funció de l'alumne, es selecciona la màxima quantitat obtinguda per algun alumne.
        nClassesImpartides_materia = (
            Impartir.objects.filter(
                controlassistencia__alumne__in=alumnes,
                horari__assignatura=assignatura,
                dia_impartir__lte=date.today(),
            )
            .values("controlassistencia__alumne")
            .annotate(hores=Count("id", distinct=True))
            .aggregate(maxval=Max("hores"))
            .get("maxval", nClassesImpartides_grup)
        )

        if (
            nClasses_grup == nClasses_materia
            or nClassesImpartides_grup == nClassesImpartides_materia
        ):
            capcelera_nFaltes.contingut = " {0}h impartides / {1}h".format(
                nClassesImpartides_grup, nClasses_grup
            )
        else:
            # Mostra les hores corresponents al professor i entre parèntesis les totals de la matèria
            capcelera_nFaltes.contingut = " {0}h({2}h) impartides / {1}h({3}h)".format(
                nClassesImpartides_grup,
                nClasses_grup,
                nClassesImpartides_materia,
                nClasses_materia,
            )

        capcelera_contacte = tools.classebuida()
        capcelera_contacte.amplade = 10
        capcelera_contacte.contingut = "Responsables"

        capcelera_observacions = tools.classebuida()
        capcelera_observacions.amplade = 10
        capcelera_observacions.contingut = "Observacions"

        taula.capceleres = [
            capcelera_foto,
            capcelera_nom,
            capcelera_nIncidencies,
            capcelera_assistencia,
            capcelera_nFaltes,
            capcelera_contacte,
        ]

        hi_ha_autoritzacions = []
        for value in CUSTOM_DADES_ADDICIONALS_ALUMNE:
            hi_ha_autoritzacions.append(value["esautoritzacio"])
        if True in hi_ha_autoritzacions:
            capcelera_autoritzacio = tools.classebuida()
            capcelera_autoritzacio.amplade = 15
            capcelera_autoritzacio.contingut = "Autorització"
            taula.capceleres.append(capcelera_autoritzacio)

        for dada in CUSTOM_DADES_ADDICIONALS_ALUMNE:
            if (
                not dada["esautoritzacio"] and "Professor" in dada["visibilitat"]
            ):  # camp no agrupable en una sóla columna i visible al professorat
                capcelera_nova = tools.classebuida()
                capcelera_nova.contingut = dada["label"]
                taula.capceleres.append(capcelera_nova)
        taula.capceleres.append(capcelera_observacions)

        taula.fileres = []
        for alumne in alumnes:
            # Per cada alumne es mostra la informació corresponent a la matèria, independentment del grup i professor.
            # Agrupa tot el corresponent a diversos professors o grups de desdoblament.

            filera = []

            # -foto------------
            camp_foto = tools.classebuida()
            camp_foto.enllac = None
            camp_foto.imatge = alumne.get_foto_or_default
            if alumne.foto:
                Accio.objects.create(
                    tipus="AS",
                    usuari=user,
                    l4=l4,
                    impersonated_from=request.user if request.user != user else None,
                    moment=datetime.now(),
                    text="""Accés a dades sensibles de l'alumne {0} per part de l'usuari {1}.""".format(
                        alumne, user
                    ),
                )

            filera.append(camp_foto)
            # -nom--------------------------------------------
            camp_nom = tools.classebuida()
            camp_nom.enllac = None
            camp_nom.contingut = "{0}".format(alumne)
            filera.append(camp_nom)

            # -incidències--------------------------------------------
            camp_nIncidencies = tools.classebuida()
            camp_nIncidencies.enllac = None
            # Selecciona totes les dades d'aquest alumne a la matèria.
            nIncidencies = alumne.incidencia_set.filter(
                # control_assistencia__impartir__horari__grup = grup,
                # control_assistencia__impartir__horari__professor = professor,
                control_assistencia__impartir__horari__assignatura=assignatura,
                tipus__es_informativa=False,
            ).count()
            nExpulsions = (
                alumne.expulsio_set.filter(
                    # control_assistencia__impartir__horari__grup = grup,
                    # control_assistencia__impartir__horari__professor = professor,
                    control_assistencia__impartir__horari__assignatura=assignatura
                )
                .exclude(estat="ES")
                .count()
            )
            camp_nIncidencies.multipleContingut = [
                (
                    "Incid:\xa0{0}".format(nIncidencies),
                    None,
                ),
                (
                    "Expul:\xa0{0}".format(nExpulsions),
                    None,
                ),
            ]
            filera.append(camp_nIncidencies)

            # -Assistencia--------------------------------------------
            from django.db.models import Count

            #                nFaltes = alumne.controlassistencia_set.filter(
            #                                                               estat__isnull = False  ,
            #                                                               impartir__horari__assignatura = assignatura
            #                                                        ).aggregate(
            #                                        ausencia = Sum( 'estat__pct_ausencia' ),
            #                                        classes = Count( 'estat' )
            #                                                        )
            # Tots els controls d'aquest alumne a la matèria.
            controls = alumne.controlassistencia_set.filter(
                impartir__dia_impartir__lte=datetime.today(),
                # impartir__horari__grup = grup,
                # impartir__horari__professor = professor,
                impartir__horari__assignatura=assignatura,
            )

            nFaltesNoJustificades = controls.filter(Q(estat__codi_estat="F")).count()
            nFaltesJustificades = controls.filter(estat__codi_estat="J").count()
            nRetards = controls.filter(estat__codi_estat="R").count()
            # calcula el 'total' de dies per alumne
            if settings.CUSTOM_NO_CONTROL_ES_PRESENCIA:
                # té en compte tots els dies encara que no s'hagi passat llista
                nControls = controls.count()
            else:
                nControls = controls.filter(estat__codi_estat__isnull=False).count()
            camp = tools.classebuida()
            camp.enllac = None
            tpc = (
                100.0
                - (
                    (100.0 * float(nFaltesNoJustificades + nFaltesJustificades))
                    / float(nControls)
                )
                if nControls > 0
                else "N/A"
            )
            camp.contingut = """{0:.2f}%""".format(tpc) if nControls > 0 else "N/A"
            filera.append(camp)

            camp = tools.classebuida()
            camp.enllac = None
            contingut = "Controls: {0},F.no J.: {1},F.Just: {2},Retards: {3}".format(
                nControls, nFaltesNoJustificades, nFaltesJustificades, nRetards
            )
            camp.multipleContingut = [
                (
                    c,
                    None,
                )
                for c in contingut.split(",")
            ]
            filera.append(camp)

            # --
            # -nom--------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            resps = alumne.get_dades_responsables()
            camp.multipleContingut = [
                (
                    resps["respPre"],
                    None,
                ),
                (
                    resps["respAlt"],
                    None,
                ),
            ]
            filera.append(camp)

            labels = [x["label"] for x in CUSTOM_DADES_ADDICIONALS_ALUMNE]
            # -Camps addicionals agrupables en una columna (autoritzacions)--------------------
            if CUSTOM_DADES_ADDICIONALS_ALUMNE and hi_ha_autoritzacions:
                camp_autoritzacio = tools.classebuida()
                camp_autoritzacio.enllac = None
                camp_autoritzacio.multipleContingut = []
                dades_addicionals_alumne = DadesAddicionalsAlumne.objects.filter(
                    alumne=alumne
                )
                for dada_addicional in dades_addicionals_alumne:
                    if dada_addicional.label in labels:
                        element = next(
                            item
                            for item in CUSTOM_DADES_ADDICIONALS_ALUMNE
                            if item["label"] == dada_addicional.label
                        )
                        agrupable = element["esautoritzacio"]
                        visible_al_professorat = "Professor" in element["visibilitat"]
                        if visible_al_professorat and agrupable:
                            camp_autoritzacio.multipleContingut.append(
                                (
                                    "{0}: {1}".format(
                                        dada_addicional.label, dada_addicional.value
                                    ),
                                    None,
                                )
                            )
                filera.append(camp_autoritzacio)

            # -Camps addicionals no agrupables en una columna --------------------
            if CUSTOM_DADES_ADDICIONALS_ALUMNE:
                camp_nou = tools.classebuida()
                camp_nou.enllac = None
                dades_addicionals_alumne = DadesAddicionalsAlumne.objects.filter(
                    alumne=alumne
                )
                for dada_addicional in dades_addicionals_alumne:
                    if dada_addicional.label in labels:
                        element = next(
                            (
                                item
                                for item in CUSTOM_DADES_ADDICIONALS_ALUMNE
                                if item["label"] == dada_addicional.label
                            ),
                            None,
                        )
                        agrupable = element["esautoritzacio"] if element else True
                        visible_al_professorat = (
                            "Professor" in element["visibilitat"] if element else False
                        )
                        if visible_al_professorat and not agrupable:
                            camp_nou.contingut = dada_addicional.value
                filera.append(camp_nou)

            # -observacions--------------------------------------------
            camp_observacions = tools.classebuida()
            camp_observacions.enllac = None
            camp_observacions.contingut = (
                "{0}".format(alumne.observacions) if alumne.observacions else ""
            )
            filera.append(camp_observacions)

            taula.fileres.append(filera)

        report.append(taula)

    return render(
        request,
        "reportTabs.html",
        {
            "report": report,
            "head": "Informació alumnes",
        },
    )


# ---------------------  --------------------------------------------#


@login_required
@group_required(["professors"])
def blanc(request):
    return render(
        request,
        "blanc.html",
        {},
    )


# ---------------- PROMOCIONS ------------------------#


@login_required
@group_required(["direcció"])
def llistaGrupsPromocionar(request):
    grups = grupsPromocionar()
    return render(request, "mostraGrupsPromocionar.html", {"grups": grups})


@login_required
@group_required(["direcció"])
def nouAlumnePromocionar(request):
    # TODO esborrar aquesta funció ?
    # Aqui va el tractament del formulari i tota la polla...

    if request.method == "POST":
        # Ve per post, he de guardar l'alumne si les dades estan correctes
        pass
    form = newAlumne()
    return render(request, "mostraFormulariPromocionar.html", {"form": form})


@login_required
@group_required(["direcció"])
def mostraGrupPromocionar(request, grup=""):
    PromoFormset = modelformset_factory(Alumne, form=promoForm, extra=0)
    if request.method == "POST":
        curs_vinent = request.POST.get("curs_desti")
        print(request.POST)
        formset = PromoFormset(request.POST)
        for form in formset.forms:
            if form.is_valid():
                decisio = form.cleaned_data["decisio"]
                if decisio == "2":
                    id = form.cleaned_data["id"].id
                    alumne = Alumne.objects.get(id=id)
                    alumne.data_baixa = date.today()
                    alumne.estat_sincronitzacio = "DEL"
                    alumne.motiu_bloqueig = "Baixa"
                    alumne.save()

                if decisio == "0" and curs_vinent:
                    id = form.cleaned_data["id"].id
                    alumne = Alumne.objects.get(id=id)
                    alumne.grup_id = curs_vinent
                    alumne.save()

        pass

    grups = grupsPromocionar()
    grup_actual = Grup.objects.get(id=grup)
    alumnes = Alumne.objects.filter(grup=grup, data_baixa__isnull=True).order_by(
        "cognoms"
    )
    if len(alumnes) == 0:
        msg = "Aquest grup no te alumnes actualment."
        return render(
            request, "mostraGrupsPromocionar.html", {"grups": grups, "msg": msg}
        )

    formset = PromoFormset(queryset=alumnes)

    return render(
        request,
        "mostraGrupPromocionar.html",
        {"grup_actual": grup_actual, "formset": formset, "grups": grups},
    )


@login_required
@group_required(["consergeria", "professors"])
def detallAlumneHorari(request, pk, detall="all"):
    from aula.apps.matricula.models import Document

    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    alumne = get_object_or_404(Alumne, pk=pk)
    professor = User2Professor(user)
    assignatura_grup = set()
    for ca in Impartir.objects.filter(horari__professor=professor):
        if ca.horari.grup is not None:
            assignatura_grup.add((ca.horari.assignatura, ca.horari.grup))
    alumnes_del_profe = set()
    for (
        assignatura,
        grup,
    ) in assignatura_grup:
        for alumn in (
            Alumne.objects.filter(
                controlassistencia__impartir__horari__grup=grup,
                controlassistencia__impartir__horari__assignatura=assignatura,
                controlassistencia__impartir__horari__professor=professor,
            )
            .distinct()
            .order_by("cognoms")
        ):
            alumnes_del_profe.add(alumn)
    es_alumne_del_profe = alumne in alumnes_del_profe
    tutors_de_lalumne = alumne.tutorsDeLAlumne()
    es_tutor_de_lalumne = professor in tutors_de_lalumne
    grups_poden_veure_detalls = [
        "sortides",
        "consergeria",
        "direcció",
    ]

    mostra_detalls = (
        es_tutor_de_lalumne
        or user.groups.filter(name__in=grups_poden_veure_detalls).exists()
    )

    data_txt = request.GET.get("data", "")
    try:
        data = datetime.strptime(data_txt, r"%Y-%m-%d").date()
    except ValueError:
        data = datetime.today()

    qAvui = Q(impartir__dia_impartir=data)
    controlOnEslAlumneAvui = alumne.controlassistencia_set.filter(qAvui)

    grup = alumne.grup
    horesDelGrupAvui = {x for x in grup.horari_set.filter(qAvui).filter(es_actiu=True)}
    horesDeAlumneAvui = {c.impartir.horari for c in controlOnEslAlumneAvui}
    horesRestants = horesDelGrupAvui - horesDeAlumneAvui

    aules = []
    for c in controlOnEslAlumneAvui:
        noHaDeSerAlAula = c.nohadeseralaula_set.all()
        missatgeNoHaDeSerAlAula = ", ".join(
            [n.get_motiu_display() for n in noHaDeSerAlAula]
        )

        estat = c.estat.nom_estat if hasattr(c.estat, "nom_estat") else ""

        horanova = True
        for aula in aules:
            if c.impartir.horari.hora == aula["hora"]:
                aula["horari_alumne"] = (
                    aula["horari_alumne"]
                    + "\n"
                    + c.impartir.get_nom_aula
                    + " "
                    + c.impartir.horari.professor.get_full_name()
                    + " "
                    + c.impartir.horari.assignatura.nom_assignatura
                    + " ("
                    + estat
                    + ")"
                )
                horanova = False
        if horanova:
            novaaula = {
                "horari_alumne": c.impartir.get_nom_aula
                + " "
                + c.impartir.horari.professor.get_full_name()
                + " "
                + c.impartir.horari.assignatura.nom_assignatura
                + " ("
                + estat
                + ")",
                "hora": c.impartir.horari.hora,
                "hora_inici": c.impartir.horari.hora.hora_inici,
                "es_horari_grup": False,
                "es_hora_actual": (
                    c.impartir.horari.hora.hora_inici
                    <= datetime.now().time()
                    <= c.impartir.horari.hora.hora_fi
                ),
                "missatge_no_ha_de_ser_a_laula": missatgeNoHaDeSerAlAula,
                "no_ha_de_ser_a_laula": True if noHaDeSerAlAula else False,
                "horari_grup": "",
            }
            aules.append(novaaula)

    for horari in horesRestants:
        horanova = True

        for aula in aules:
            if horari.hora == aula["hora"]:
                aula["horari_grup"] = (
                    aula["horari_grup"]
                    + "\n"
                    + horari.nom_aula
                    + " "
                    + unicode(horari.professor)
                    + " "
                    + unicode(horari.assignatura)
                )
                horanova = False
        if horanova:
            novaaula = {
                "horari_alumne": "",
                "hora": horari.hora,
                "hora_inici": horari.hora.hora_inici,
                "es_horari_grup": True,
                "es_hora_actual": (
                    horari.hora.hora_inici
                    <= datetime.now().time()
                    <= horari.hora.hora_fi
                ),
                "no_ha_de_ser_a_laula": "",
                "horari_grup": (
                    horari.nom_aula
                    + " "
                    + unicode(horari.professor)
                    + " "
                    + unicode(horari.assignatura)
                ),
            }
            aules.append(novaaula)

    aules_sorted = sorted(aules, key=lambda x: x["hora_inici"])
    table = HorariAlumneTable(aules_sorted)
    table.order_by = "hora_inici"

    RequestConfig(request).configure(table)
    if alumne.foto:
        Accio.objects.create(
            tipus="AS",
            usuari=user,
            l4=l4,
            impersonated_from=request.user if request.user != user else None,
            moment=datetime.now(),
            text="""Accés a dades sensibles de l'alumne {0} per part de l'usuari {1}.""".format(
                alumne, user
            ),
        )

    if user.groups.filter(name__in=["direcció"]).exists():
        documents = Document.objects.filter(matricula__alumne=alumne).order_by("pk")
    else:
        documents = []

    return render(
        request,
        "mostraInfoAlumneCercat.html",
        {
            "table": table,
            "alumne": alumne,
            "dia": data,
            "mostra_detalls": mostra_detalls,
            "lendema": (data + timedelta(days=+1)).strftime(r"%Y-%m-%d"),
            "avui": datetime.today().date().strftime(r"%Y-%m-%d"),
            "diaabans": (data + timedelta(days=-1)).strftime(r"%Y-%m-%d"),
            "ruta_fotos": settings.PRIVATE_STORAGE_ROOT,
            "es_professor": es_alumne_del_profe,
            "documents": documents,
        },
    )


@login_required
@group_required(
    [
        "professional",
        "consergeria",
    ]
)
def cercaUsuari(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    if request.method == "POST":
        formUsuari = triaAlumneSelect2Form(
            request.POST
        )  # todo: multiple=True (multiples alumnes de cop)
        if formUsuari.is_valid():
            alumne = formUsuari.cleaned_data["alumne"]
            next_url = r"/alumnes/detallAlumneHorari/{0}/all/"
            return HttpResponseRedirect(next_url.format(alumne.pk))

    else:
        formUsuari = triaAlumneSelect2Form()
    return render(request, "form.html", {"form": formUsuari, "head": "Triar usuari"})


# amorilla@xtec.cat
@login_required
@group_required(["direcció"])
def llistaAlumnescsv(request):
    """
    Generates an Excel spreadsheet for review by a staff member.
    """
    ara = datetime.now()
    q_no_es_baixa = Q(data_baixa__gt=ara) | Q(data_baixa__isnull=True)

    llistaAlumnes = Alumne.objects.filter(q_no_es_baixa).order_by(
        "grup__descripcio_grup", "cognoms", "nom"
    )

    dades = [
        [
            e.ralc,
            (unicode(e.grup) + " - " + e.cognoms + ", " + e.nom),
            e.grup,
            e.cognoms,
            e.nom,
            e.user_associat.username,
            e.get_correu_relacio(),
            (
                e.get_responsables(compatible=True)[0].get_correu_relacio()
                if e.get_responsables(compatible=True)[0]
                else ""
            ),
            (
                e.get_responsables(compatible=True)[1].get_correu_relacio()
                if e.get_responsables(compatible=True)[1]
                else ""
            ),
            ",".join(e.get_correus_tots()),
            e.esta_relacio_familia_actiu(),
            bool(e.get_correus_relacio_familia()),
        ]
        for e in llistaAlumnes
    ]

    capcelera = [
        "ralc",
        "alumne",
        "grup",
        "cognoms",
        "nom",
        "username",
        "correu",
        "correu relació família 1",
        "correu relació família 2",
        "tots els correus",
        "usuari actiu",
        "correus OK",
    ]

    template = loader.get_template("export.csv")
    context = {
        "capcelera": capcelera,
        "dades": dades,
    }

    response = HttpResponse()
    filename = "llistaAlumnes.csv"

    response["Content-Disposition"] = "attachment; filename=" + filename
    response["Content-Type"] = "text/csv; charset=utf-8"
    # response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    # Add UTF-8 'BOM' signature, otherwise Excel will assume the CSV file
    # encoding is ANSI and special characters will be mangled
    response.write(template.render(context))

    return response
