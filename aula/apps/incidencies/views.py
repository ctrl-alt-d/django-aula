# This Python file uses the following encoding: utf-8
import itertools

# dates
from datetime import date, datetime, timedelta
from itertools import groupby

from django.apps import apps
from django.conf import settings
from django.contrib import messages

# consultes
# from django.db.models import Q
# auth
from django.contrib.auth.decorators import login_required

# excepcions
from django.core.exceptions import NON_FIELD_ERRORS, ObjectDoesNotExist, ValidationError
from django.db.models import Q
from django.db.models.deletion import ProtectedError

# helpers
from django.forms.models import modelform_factory

# workflow
from django.http import Http404, HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, render

# templates
from django.template import loader
from django.utils.text import slugify
from django_tables2 import RequestConfig

from aula.apps.alumnes.forms import triaAlumneNomSentitSelect2Form
from aula.apps.alumnes.models import Alumne, AlumneNomSentit
from aula.apps.horaris.models import DiaDeLaSetmana, FranjaHoraria
from aula.apps.incidencies.business_rules.expulsio import expulsio_despres_de_posar
from aula.apps.incidencies.business_rules.incidencia import incidencia_despres_de_posar

# formularis
from aula.apps.incidencies.forms import (
    incidenciesRelacionadesForm,
    posaExpulsioForm,
    posaExpulsioFormW2,
    posaIncidenciaAulaForm,
)
from aula.apps.incidencies.helpers import preescriu
from aula.apps.incidencies.models import (
    Expulsio,
    Incidencia,
    Sancio,
    TipusIncidencia,
    TipusSancio,
)
from aula.apps.incidencies.table2_models import (
    Table2_AlertesAcumulacioExpulsions,
    Table2_ExpulsionsIIncidenciesPerAlumne,
    Table2_ExpulsionsPendentsPerAcumulacio,
    Table2_ExpulsionsPendentsTramitar,
    Table2_ExpulsioTramitar,
)

# models
from aula.apps.presencia.models import ControlAssistencia, Impartir
from aula.apps.presenciaSetmanal.views import ProfeNoPot
from aula.apps.usuaris.models import (
    Accio,
    Professional,
    Professor,
    User2Professional,
    User2Professor,
    User2ProfessorConserge,
)
from aula.utils import tools
from aula.utils.decorators import group_required
from aula.utils.forms import ckbxForm
from aula.utils.my_paginator import DiggPaginator
from aula.utils.tools import unicode
from aula.utils.widgets import DateTextImput, DateTimeTextImput


# vistes -----------------------------------------------------------------------------------
@login_required
@group_required(["professors"])
def posaIncidenciaAula(request, pk):  # pk = pk_impartir
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    impartir = get_object_or_404(Impartir, pk=pk)

    head = "Incidències aula " + unicode(impartir)

    # Posa incidències
    alumnes = AlumneNomSentit.objects.filter(
        pk__in=[ca.alumne.pk for ca in impartir.controlassistencia_set.all()]
    )

    if request.method == "POST":
        form = posaIncidenciaAulaForm(
            request.POST, queryset=alumnes, etiqueta="Posar incidència a:"
        )

        if form.is_valid():
            alumnes_amb_incidencia = form.cleaned_data["alumnes"]
            frases_de_la_bdd = form.cleaned_data["frases"]
            frase_manual = form.cleaned_data["frase"]
            tipus = form.cleaned_data["tipus"]
            totes_les_frases = [frase.frase for frase in frases_de_la_bdd] + (
                [frase_manual] if frase_manual else []
            )

            s_ha_pogut_crear_la_incidencia = False
            for alumne_amb_incidencia in alumnes_amb_incidencia:
                for frase in totes_les_frases:
                    try:
                        control_assistencia = impartir.controlassistencia_set.get(
                            alumne=alumne_amb_incidencia
                        )
                        incidencia, created = Incidencia.objects.get_or_create(
                            professional=User2Professional(user),
                            control_assistencia=control_assistencia,
                            alumne=alumne_amb_incidencia,
                            descripcio_incidencia=frase,
                            tipus=tipus,
                        )
                        #                                                es_informativa = es_informativa )
                        s_ha_pogut_crear_la_incidencia = True
                        if created:
                            # LOGGING
                            Accio.objects.create(
                                tipus="IN",
                                usuari=user,
                                l4=l4,
                                impersonated_from=(
                                    request.user if request.user != user else None
                                ),
                                text="""Posada incidència a l'alumne {0}. Text incidència: {1}""".format(
                                    incidencia.alumne, incidencia.descripcio_incidencia
                                ),
                            )
                            incidencia_despres_de_posar(incidencia)

                    except ValidationError as e:
                        # Com que no és un formulari de model cal tractar a mà les incidències del save:
                        for _, v in e.message_dict.items():
                            form._errors.setdefault(NON_FIELD_ERRORS, []).extend(v)

            if not s_ha_pogut_crear_la_incidencia:
                form._errors.setdefault(NON_FIELD_ERRORS, []).append(
                    """No s'ha pogut crear la incidència.
                                    Comprova que has seleccionat al menys un alumne i una frase"""
                )
            else:
                # netejo el formulari per que no quedi marcat alumne i falta.
                form = posaIncidenciaAulaForm(
                    queryset=alumnes, etiqueta="Posar incidència a"
                )

    else:
        form = posaIncidenciaAulaForm(queryset=alumnes, etiqueta="Posar incidència a")

    # Recull incidències ( i permet afegir-ne més)
    incidenciesAgrupades = {}
    for control_assistencia in impartir.controlassistencia_set.all():
        for incidencia in control_assistencia.incidencia_set.all():
            agrupacio = (incidencia.tipus.tipus, incidencia.descripcio_incidencia)
            #            incidenciesAgrupades.setdefault(agrupacio, []) .append(  incidencia  )
            incidenciesAgrupades.setdefault(agrupacio, [])
            incidenciesAgrupades[agrupacio].append(incidencia)

    # Expulsion
    expulsions = []
    for control_assistencia in impartir.controlassistencia_set.all():
        for expulsio in control_assistencia.expulsio_set.all():
            expulsions.append(expulsio)

    for f in ["frases", "frase", "alumnes"]:
        form.fields[f].widget.attrs["class"] = "form-control " + form.fields[
            f
        ].widget.attrs.get("class", "")

    return render(
        request,
        "posaIncidenciaAula.html",
        {
            "form": form,
            "incidenciesAgrupades": incidenciesAgrupades,
            "expulsions": expulsions,
            "id_impartir": pk,
            "head": head,
        },
    )


@login_required
@group_required(["professors"])
def eliminaIncidenciaAula(request, pk):  # pk = pk_incidencia
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    es_consultable = True
    try:
        incidencia = Incidencia.objects.get(pk=pk)
    except Incidencia.DoesNotExist:
        es_consultable = False

    try:
        # la incidència ha de ser d'aula:
        pk_impartir = incidencia.control_assistencia.impartir.pk
    except:  # noqa: E722
        es_consultable = False

    if not es_consultable:
        return render(
            request,
            "resultat.html",
            {
                "head": "Error eliminant incidència.",
                "msgs": {
                    "errors": [],
                    "warnings": ["Aquesta incidència ja no existeix"],
                    "infos": [],
                },
            },
        )

    url_next = "/incidencies/posaIncidenciaAula/%s/" % (pk_impartir)
    try:
        incidencia.credentials = credentials
        incidencia.delete()
        # LOGGING
        Accio.objects.create(
            tipus="IN",
            usuari=user,
            l4=l4,
            impersonated_from=request.user if request.user != user else None,
            text="""Eliminada incidència d'aula de l'alumne {0}. Text incidència: {1}""".format(
                incidencia.alumne, incidencia.descripcio_incidencia
            ),
        )

    except ValidationError as e:
        resultat = {
            "errors": list(itertools.chain(*e.message_dict.values())),
            "warnings": [],
            "infos": [],
            "url_next": url_next,
        }
        return render(
            request,
            "resultat.html",
            {"head": "Error a l'esborrar incidència d 'aula", "msgs": resultat},
        )

    return HttpResponseRedirect(url_next)


@login_required
@group_required(["professors", "professional"])
def eliminaIncidencia(request, pk):  # pk = pk_incidencia
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    try:
        incidencia = Incidencia.objects.get(pk=pk)
    except:  # noqa: E722
        return render(
            request,
            "resultat.html",
            {
                "head": "Error eliminant incidència",
                "msgs": {
                    "errors": [],
                    "warnings": ["Aquesta incidència ja no existeix"],
                    "infos": [],
                },
            },
        )

    incidencia.credentials = credentials

    origen = request.GET.get("origen", None)
    if origen == "tutoria":
        url_next = "/tutoria/incidenciesGestionadesPelTutor/"
    else:
        url_next = "/incidencies/llistaIncidenciesProfessional/"
    try:
        incidencia.delete()
        # LOGGING
        Accio.objects.create(
            tipus="IN",
            usuari=user,
            l4=l4,
            impersonated_from=request.user if request.user != user else None,
            text="""Eliminada incidència de l'alumne {0}. Text incidència: {1}""".format(
                incidencia.alumne, incidencia.descripcio_incidencia
            ),
        )
        messages.success(
            request,
            "Incidència de l'alumne {alumne} esborrada correctament".format(
                alumne=incidencia.alumne
            ),
        )
    except ValidationError as e:
        resultat = {
            "errors": list(itertools.chain(*e.message_dict.values())),
            "warnings": [],
            "infos": [],
            "url_next": url_next,
        }
        return render(
            request,
            "resultat.html",
            {"head": "Error a l'esborrar incidència d 'aula", "msgs": resultat},
        )

    return HttpResponseRedirect(url_next)


# dev novaEntrevista( request, pk ):
# https://docs.djangoproject.com/en/dev/ref/contrib/formtools/form-wizard/

# vistes -----------------------------------------------------------------------------------


@login_required
@group_required(["professors", "professional"])
def posaIncidencia(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    missatge = ""

    formIncidenciaF = modelform_factory(
        Incidencia,
        fields=[
            "dia_incidencia",
            "franja_incidencia",
            "tipus",
            #                                                            'es_informativa'])
            "descripcio_incidencia",
        ],
    )
    formIncidenciaF.base_fields["dia_incidencia"].widget = DateTextImput()

    formset = []
    if request.method == "POST":
        # formAlumne = triaAlumneForm(request.POST ) #todo: multiple=True (multiples alumnes de cop)
        formAlumne = triaAlumneNomSentitSelect2Form(
            request.POST
        )  # todo: multiple=True (multiples alumnes de cop)
        incidencia = Incidencia(es_vigent=True)
        incidencia.professional = User2Professional(user)
        incidencia.credentials = credentials
        formIncidencia = formIncidenciaF(request.POST, instance=incidencia)
        if formAlumne.is_valid():
            alumne = formAlumne.cleaned_data["alumne"]
            incidencia.alumne = alumne
            if formIncidencia.is_valid():
                incidencia = formIncidencia.save()

                # LOGGING
                Accio.objects.create(
                    tipus="IN",
                    usuari=user,
                    l4=l4,
                    impersonated_from=request.user if request.user != user else None,
                    text="""Posar incidència a {0}. Text incidència: {1}""".format(
                        alumne, incidencia.descripcio_incidencia
                    ),
                )

                incidencia_despres_de_posar(incidencia)
                missatge = "Incidència anotada"
                messages.info(request, missatge)
                url = "/incidencies/llistaIncidenciesProfessional/#alumne-{0}".format(
                    incidencia.alumne.pk
                )

                return HttpResponseRedirect(url)

        #                    incidencia = formIncidencia.save(commit = False )
        #                    try:
        #                        incidencia.save()
        #                    except ValidationError, e:
        #                        formIncidencia._errors = {}
        #                        for _, v in e.message_dict.items():
        #                            formIncidencia._errors.setdefault(NON_FIELD_ERRORS, []).extend(  v  )
        #                    else:
        #                        Incidencia_despres_de_posar( incidencia )
        #                        url = '/incidencies/llistaIncidenciesProfessional'  #todo: a la pantalla d''incidencies
        #                        return HttpResponseRedirect( url )
        #                    return HttpResponseRedirect( url )

        formset.append(formAlumne)
        formset.append(formIncidencia)

    else:
        # formAlumne = triaAlumneForm( ) #todo: multiple=True (multiples alumnes de cop)
        formAlumne = triaAlumneNomSentitSelect2Form()
        #        formIncidenciaF = modelform_factory(Incidencia, fields=['dia_incidencia',
        #                                                                'franja_incidencia',
        #                                                                'descripcio_incidencia',
        #                                                                'es_informativa'])
        #        formIncidenciaF.base_fields['dia_incidencia'].widget =  DateTextImput()
        formIncidencia = formIncidenciaF()

        formset.append(formAlumne)
        formset.append(formIncidencia)

    for f in ["descripcio_incidencia"]:  # , 'franja_incidencia', 'tipus' ]:
        formIncidencia.fields[f].widget.attrs["class"] = (
            "form-control " + formIncidencia.fields[f].widget.attrs.get("class", "")
        )

    return render(
        request,
        "formset.html",
        {"formset": formset, "head": "Incidència", "missatge": missatge},
    )


# Incidència per primera hora:


@login_required
@group_required(["consergeria"])
def posaIncidenciaPrimeraHora(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    missatge = ""

    #
    formIncidenciaF = modelform_factory(
        Incidencia,
        fields=[
            "dia_incidencia",
            "franja_incidencia",
        ],
    )
    formIncidenciaF.base_fields["dia_incidencia"].widget = DateTextImput()

    #
    tipus_incidencia = TipusIncidencia.objects.filter(es_informativa=False).first()
    if not bool(tipus_incidencia):
        messages.error(
            request,
            "Cal entrar el tipus 'Incidència' des d'admin. Crida a l'administrador del sistema.",
        )
        url = "/incidencies/posaIncidenciaprimerahora"
        return HttpResponseRedirect(url)

    #
    ara = datetime.now().time()
    franja = FranjaHoraria.objects.filter(hora_inici__lte=ara, hora_fi__gte=ara).first()
    conserge_inicia = User2ProfessorConserge(user)
    incidencia = Incidencia(
        dia_incidencia=datetime.today(),
        tipus=tipus_incidencia,
        franja_incidencia=franja,
        descripcio_incidencia="Retard en entrar al Centre",
        gestionada_pel_tutor=True,
        gestionada_pel_tutor_motiu=Incidencia.GESTIONADA_PEL_TUTOR_RETARD_PRIMERA_HORA,
        professional_inicia=conserge_inicia,
    )

    #
    formset = []
    if request.method == "POST":
        formAlumne = triaAlumneNomSentitSelect2Form(request.POST)

        incidencia.credentials = credentials
        formIncidencia = formIncidenciaF(request.POST, instance=incidencia)
        if formAlumne.is_valid():
            alumne = formAlumne.cleaned_data["alumne"]
            incidencia.alumne = alumne
            incidencia.professional = (
                alumne.tutorsDelGrupDeLAlumne().first()
                if alumne.tutorsDelGrupDeLAlumne()
                else alumne.tutorsIndividualitzatsDeLAlumne().first()
            )

            try:
                if not bool(incidencia.professional):
                    messages.error(request, "No s'han trobat tutors per aquest alumne")
                    url = "/incidencies/posaIncidenciaprimerahora"
                    return HttpResponseRedirect(url)
            except ObjectDoesNotExist:
                messages.error(request, "No s'han trobat tutors per aquest alumne")
                url = "/incidencies/posaIncidenciaprimerahora"
                return HttpResponseRedirect(url)

            if formIncidencia.is_valid():
                incidencia = formIncidencia.save()

                # LOGGING
                Accio.objects.create(
                    tipus="IN",
                    usuari=user,
                    l4=l4,
                    impersonated_from=request.user if request.user != user else None,
                    text="""Posar incidència a {0}. Text incidència: {1}""".format(
                        alumne, incidencia.descripcio_incidencia
                    ),
                )

                incidencia_despres_de_posar(incidencia)
                missatge = "Incidència anotada."
                messages.info(request, missatge)
                url = "/incidencies/posaIncidenciaprimerahora"

                return HttpResponseRedirect(url)

        formset.append(formAlumne)
        formset.append(formIncidencia)

    else:
        formAlumne = triaAlumneNomSentitSelect2Form()
        formIncidencia = formIncidenciaF(instance=incidencia)

        formset.append(formAlumne)
        formset.append(formIncidencia)

    return render(
        request,
        "formset.html",
        {
            "formset": formset,
            "titol_formulari": "Incidència per retard entrada al centre",
            "missatge": missatge,
        },
    )


# vistes -----------------------------------------------------------------------------------


@login_required
@group_required(["professors"])
def posaExpulsio(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    formset = []
    if request.method == "POST":
        expulsio = Expulsio()
        expulsio.credentials = credentials
        expulsio.professor_recull = User2Professor(user)

        # formAlumne = triaAlumneForm(request.POST )
        formAlumne = triaAlumneNomSentitSelect2Form(request.POST)
        formExpulsio = posaExpulsioForm(data=request.POST, instance=expulsio)

        if formAlumne.is_valid():
            expulsio.alumne = formAlumne.cleaned_data["alumne"]
            if formExpulsio.is_valid():
                expulsio.save()

                url = "/incidencies/posaExpulsioW2/{u}".format(u=expulsio.pk)

                return HttpResponseRedirect(url)

        else:
            formset.append(formAlumne)
            formset.append(formExpulsio)

    else:
        # formAlumne = triaAlumneForm( )
        formAlumne = triaAlumneNomSentitSelect2Form()

        franja_actual = None
        try:
            from aula.apps.horaris.models import FranjaHoraria

            franja_actual = (
                FranjaHoraria.objects.filter(hora_inici__lte=datetime.now())
                .filter(hora_fi__gte=datetime.now())
                .get()
            )
        except:  # noqa: E722
            pass

        formExpulsio = posaExpulsioForm(
            initial={"franja_expulsio": franja_actual, "dia_expulsio": datetime.today()}
        )

        formset.append(formAlumne)
        formset.append(formExpulsio)

    return render(
        request,
        "formset.html",
        {
            "formset": formset,
            "head": "Recullir Expulsió (Pas 1/2)",
        },
    )


@login_required
@group_required(["professors"])
def posaExpulsioW2(request, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    expulsio = get_object_or_404(Expulsio, pk=pk)

    # seg---------
    if (
        not (l4 or expulsio.professor_recull.getUser().pk == user.pk)
        or expulsio.estat != "ES"
    ):
        raise Http404()

    expulsio.credentials = credentials

    infoForm = [
        ("Alumne", unicode(expulsio.alumne)),
        ("Hora", expulsio.franja_expulsio),
    ]

    # Miro quin podria ser el professor:
    q_alumne = Q(alumne=expulsio.alumne)
    q_dia = Q(impartir__dia_impartir=expulsio.dia_expulsio)
    q_franja = Q(impartir__horari__hora=expulsio.franja_expulsio)

    possible_control_assistencia = None
    possible_professor = None
    possibles_professors = []

    possibles_controls_assistencia = ControlAssistencia.objects.filter(
        q_alumne & q_dia & q_franja
    ).order_by()
    if possibles_controls_assistencia.exists():
        possible_control_assistencia = possibles_controls_assistencia[0]

        possible_professor = (
            possible_control_assistencia.impartir.professor_passa_llista
            or possible_control_assistencia.impartir.professor_guardia
            or possible_control_assistencia.impartir.horari.professor
        )

        if possible_control_assistencia.impartir.professor_passa_llista is not None:
            possibles_professors.append(
                possible_control_assistencia.impartir.professor_passa_llista
            )

        if possible_control_assistencia.impartir.professor_guardia is not None:
            possibles_professors.append(
                possible_control_assistencia.impartir.professor_guardia
            )

        if possible_control_assistencia.impartir.horari.professor is not None:
            possibles_professors.append(
                possible_control_assistencia.impartir.horari.professor
            )

    if request.method == "POST":
        formExpulsio = posaExpulsioFormW2(request.POST, instance=expulsio)
        formExpulsio.instance.estat = "AS"
        if formExpulsio.is_valid():
            expulsio = formExpulsio.save(commit=False)
            if expulsio.professor in possibles_professors:
                expulsio.control_assistencia = possible_control_assistencia

            expulsio.save()

            # LOGGING
            Accio.objects.create(
                tipus="RE",
                usuari=user,
                l4=l4,
                impersonated_from=request.user if request.user != user else None,
                text="""Recullir expulsió d'alumne {0}. Professor que expulsa: {1}""".format(
                    expulsio.alumne, expulsio.professor
                ),
            )

            expulsio_despres_de_posar(expulsio)
            url = "/missatgeria/elMeuMur/"
            messages.info(request, "L'expulsió ha estat anotada")
            return HttpResponseRedirect(url)

    else:
        if possible_control_assistencia is None:
            infoForm.append(
                (
                    "Assignatura",
                    """Aquest alumne no està assignat a cap classe a aquesta hora""",
                )
            )
        else:
            infoForm.append(
                (
                    "Assignatura",
                    possible_control_assistencia.impartir.horari.assignatura,
                )
            )

        # TODO: Si no està a cap llista cal informar-ho!!
        formExpulsio = posaExpulsioFormW2(
            instance=expulsio, initial={"professor": possible_professor}
        )

    return render(
        request,
        "form.html",
        {
            "form": formExpulsio,
            "infoForm": infoForm,
            "head": "Recullir Expulsió (Pas 2/2)",
        },
    )


@login_required
@group_required(["professors"])
def editaExpulsio(request, pk):
    # from incidencies.forms import editaExpulsioForm

    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    expulsio = get_object_or_404(Expulsio, pk=pk)

    # seg---------
    pot_entrar = (
        l4
        or (expulsio.professor is not None and expulsio.professor.pk == user.pk)
        or user.groups.filter(name="direcció").exists()
    )
    if not pot_entrar:
        raise Http404()

    expulsio.credentials = credentials

    edatAlumne = None
    try:
        edatAlumne = expulsio.alumne.edat()
    except:  # noqa: E722
        pass

    resps = expulsio.alumne.get_dades_responsables()

    infoForm = [
        ("Alumne", unicode(expulsio.alumne)),
        ("Edat alumne", edatAlumne),
        ("Dia", expulsio.dia_expulsio),
        ("Hora", expulsio.franja_expulsio),
        ("Responsable preferent", resps["respPre"]),
        ("Responsable (altre)", resps["respAlt"]),
        ("Altres telèfons", expulsio.alumne.get_telefons()),
        ("Professor que expulsa", expulsio.professor if expulsio.professor else "N/A"),
        (
            "Professor que recull expulsió",
            expulsio.professor_recull if expulsio.professor_recull else "N/A",
        ),
    ]

    fields = [
        "motiu",
        "tutor_contactat_per_l_expulsio",
        "moment_comunicacio_a_tutors",
        "tramitacio_finalitzada",
    ]
    if l4:
        fields.extend(
            [
                "professor_recull",
                "dia_expulsio",
                "franja_expulsio",
                "provoca_sancio",
                "es_vigent",
            ]
        )

    widgets = {"moment_comunicacio_a_tutors": DateTimeTextImput()}
    editaExpulsioFormF = modelform_factory(Expulsio, fields=fields, widgets=widgets)
    # editaExpulsioFormF.base_fields['moment_comunicacio_a_tutors'].widget = forms.DateTimeInput(attrs={'class':'datepickerT'} )

    try:
        editaExpulsioFormF.base_fields["dia_expulsio"].widget = DateTextImput()
    except:  # noqa: E722
        pass

    if request.method == "POST":
        # TODO: Canviar per una factoria: mirar actuacions.
        formExpulsio = editaExpulsioFormF(data=request.POST, instance=expulsio)
        can_delete = ckbxForm(
            data=request.POST,
            label="Esborrar expulsió",
            help_text="""Marca aquesta casella per esborrar aquesta expulsió""",
        )

        if formExpulsio.is_valid() and can_delete.is_valid():
            hiHaErrors = False
            if can_delete.cleaned_data["ckbx"] and l4:
                try:
                    expulsio.incidencia_set.update(provoca_expulsio=None)
                    expulsio.delete()
                    # LOGGING
                    Accio.objects.create(
                        tipus="EE",
                        usuari=user,
                        l4=l4,
                        impersonated_from=(
                            request.user if request.user != user else None
                        ),
                        text="""Esborrada expulsió d'alumne {0}.""".format(
                            expulsio.alumne
                        ),
                    )
                except ValidationError as e:
                    hiHaErrors = True
                    for m in itertools.chain(*e.message_dict.values()):
                        messages.error(unicode(m))
                    for _, v in e.message_dict.items():
                        formExpulsio._errors.setdefault(NON_FIELD_ERRORS, []).extend(v)
            else:
                expulsio.save()
                # LOGGING
                Accio.objects.create(
                    tipus="EE",
                    usuari=user,
                    l4=l4,
                    impersonated_from=request.user if request.user != user else None,
                    text="""Editada expulsió d'alumne {0}.""".format(expulsio.alumne),
                )
            if not hiHaErrors:
                url = "/incidencies/llistaIncidenciesProfessional/"
                return HttpResponseRedirect(url)

    else:
        formExpulsio = editaExpulsioFormF(instance=expulsio)
        can_delete = ckbxForm(
            data=request.POST,
            label="Esborrar expulsió:",
            help_text="""Marca aquesta cassella per esborrar aquesta expulsió""",
        )

    formExpulsio.infoForm = infoForm
    formset = [formExpulsio]
    formset.extend([can_delete] if l4 else [])

    #
    for f in [
        "motiu",
        "tutor_contactat_per_l_expulsio",
        "moment_comunicacio_a_tutors",
        "tramitacio_finalitzada",
    ]:
        formExpulsio.fields[f].widget.attrs["class"] = (
            "form-control " + formExpulsio.fields[f].widget.attrs.get("class", "")
        )
    return render(
        request,
        "formset.html",
        {
            "formset": formset,
            "infoForm": infoForm,
            "head": "Expulsió",
        },
    )


# --------------------------------------------------------------------------------------------------


@login_required
@group_required(["professors"])
def posaExpulsioPerAcumulacio(request, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    incidencia = get_object_or_404(Incidencia, pk=pk)

    url_incidencies_tutoria = "/tutoria/incidenciesGestionadesPelTutor/"
    url_totes_les_incidencies = "/incidencies/llistaIncidenciesProfessional/"
    origen = request.GET.get("origen", None)
    if origen == "tutoria":
        url_next_default = url_incidencies_tutoria
    else:
        url_next_default = url_totes_les_incidencies

    professional = incidencia.professional
    User2Professor(professional.getUser())

    # -seg---------
    te_permis = (
        l4
        or user.pk == professional.pk
        or user.pk in [p.pk for p in incidencia.alumne.tutorsDeLAlumne()]
    )
    if not te_permis:
        raise Http404()

    # -ja ha generat l'expulsió---
    if incidencia.provoca_expulsio:
        messages.warning(request, "Aquesta incidència ja havia generat una expulsió")
        url_next = "/incidencies/editaExpulsio/{0}/".format(
            incidencia.provoca_expulsio.pk
        )
        return HttpResponseRedirect(url_next)

    # - o bé es gestionada pel tutor o bé és d'un professor.
    alumne = incidencia.alumne
    incidencies = alumne.incidencia_set.filter(
        es_vigent=True,
        tipus__es_informativa=False,
    )
    # -- És gestionada pel tutor
    incidencies_gestionades_tutor = incidencies.filter(gestionada_pel_tutor=True)
    n_incidencies_gestionades_tutor = incidencies_gestionades_tutor.count()
    te_3_incidencies_gestionades_pel_tutor = (
        n_incidencies_gestionades_tutor >= 3
        and user.pk in [p.pk for p in incidencia.alumne.tutorsDeLAlumne()]
    )
    if te_3_incidencies_gestionades_pel_tutor:
        incidencies = incidencies_gestionades_tutor

    # -- Tres incidències d'un mateix professor
    if not te_3_incidencies_gestionades_pel_tutor:
        incidencies_mateix_professor = incidencies.filter(professional=professional)
        n_incidencies_mateix_professor = incidencies_mateix_professor.count()
        te_3_incidencies_mateix_professor = n_incidencies_mateix_professor >= 3
        if te_3_incidencies_mateix_professor:
            incidencies = incidencies_mateix_professor

    # -- Passem a fer l'expulsió
    podem_fer_expulsio = (
        te_3_incidencies_gestionades_pel_tutor or te_3_incidencies_mateix_professor
    )

    if not podem_fer_expulsio:
        messages.warning(request, "No podem fer expulsió.")
        return HttpResponseRedirect(url_next_default)

    alumne = incidencia.alumne
    professor_recull = User2Professor(user)

    str_incidencies = ", ".join(
        [
            "{0} ({1})".format(i.descripcio_incidencia, i.dia_incidencia)
            for i in incidencies
        ]
    )
    gestionada_pel_tutor_txt = (
        "\n(Incidència gestionada pel tutor)"
        if te_3_incidencies_gestionades_pel_tutor
        else ""
    )
    motiu_san = """Expulsió per acumulació d'incidències: {0} {1}""".format(
        str_incidencies, gestionada_pel_tutor_txt
    )

    try:
        expulsio = Expulsio.objects.create(
            estat="AS",
            professor_recull=professor_recull,
            professor=professor_recull,
            alumne=alumne,
            dia_expulsio=incidencia.dia_incidencia,
            franja_expulsio=incidencia.franja_incidencia,
            motiu=motiu_san,
            es_expulsio_per_acumulacio_incidencies=True,
        )

        # LOGGING
        Accio.objects.create(
            tipus="EE",
            usuari=user,
            l4=l4,
            impersonated_from=request.user if request.user != user else None,
            text="""Creada expulsió d'alumne {0} per acumulació d'incidències.""".format(
                expulsio.alumne
            ),
        )

        expulsio_despres_de_posar(expulsio)
        incidencies.update(es_vigent=False, provoca_expulsio=expulsio)
        missatge = (
            """Generada expulsió per acumulació d'incidències. Alumne/a: {0} """.format(
                expulsio.alumne
            )
        )
        messages.info(request, missatge)

    except ValidationError as e:
        messages.error(request, ", ".join(itertools.chain(*e.message_dict.values())))
        return HttpResponseRedirect(url_next_default)

    return HttpResponseRedirect(url_totes_les_incidencies)


# --------------------------------------------------------------------------------------------------


@login_required
@group_required(["professors", "professional"])
def llistaIncidenciesProfessional(request):
    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    professional = get_object_or_404(Professional, pk=user.pk)
    professor = get_object_or_404(
        Professor, pk=user.pk
    )  # TODO: compte, Han de poder entrar els no professors!

    unicode(professional)

    # TODO: Deixar entrar a l'equip directiu
    if user != professor.getUser():
        return HttpResponseRedirect("/")

    # Expulsions pendents:
    expulsionsPendentsTramitar = [
        expulsio
        for expulsio in professor.expulsio_set.exclude(tramitacio_finalitzada=True)
    ]

    expulsionsPendentsPerAcumulacio = []

    # alumne -> incidencies i expulsions
    alumnes = {}
    for incidencia in professional.incidencia_set.all():
        alumne_str = unicode(incidencia.alumne)
        # dia_prescriu_incidencia = date.today() - timedelta( days = settings.CUSTOM_DIES_PRESCRIU_INCIDENCIA )
        incidenciesAlumne = incidencia.alumne.incidencia_set.filter(
            professional=professional,
            es_vigent=True,
            tipus__es_informativa=False,
            gestionada_pel_tutor=False,
            # dia_incidencia__gte = dia_prescriu_incidencia
        )
        calTramitarExpulsioPerAcumulacio = (
            settings.CUSTOM_INCIDENCIES_PROVOQUEN_EXPULSIO
            and incidenciesAlumne.count() >= 3
        )
        exempleIncidenciaPerAcumulacio = (
            incidenciesAlumne.order_by("dia_incidencia").reverse()[0]
            if calTramitarExpulsioPerAcumulacio
            else None
        )
        if calTramitarExpulsioPerAcumulacio and alumne_str not in alumnes:
            exempleIncidenciaPerAcumulacio.aux_origen = "professional"
            expulsionsPendentsPerAcumulacio.append(exempleIncidenciaPerAcumulacio)

        alumnes.setdefault(
            alumne_str,
            {
                "calTramitarExpulsioPerAcumulacio": calTramitarExpulsioPerAcumulacio,
                "exempleIncidenciaPerAcumulacio": exempleIncidenciaPerAcumulacio,
                "alumne": incidencia.alumne,
                "grup": incidencia.alumne.grup,
                "incidencies": [],
                "expulsions": [],
            },
        )
        alumnes[alumne_str]["incidencies"].append(incidencia)

    for expulsio in professor.expulsio_set.all():
        alumne_str = unicode(expulsio.alumne)
        alumnes.setdefault(
            alumne_str,
            {
                "alumne": expulsio.alumne,
                "grup": expulsio.alumne.grup,
                "incidencies": [],
                "expulsions": [],
            },
        )
        alumnes[alumne_str]["expulsions"].append(expulsio)

    alumnesOrdenats = [
        (
            alumneKey,
            alumnes[alumneKey],
        )
        for alumneKey in sorted(iter(alumnes.keys()))
    ]

    # table = Table2_IncidenciesMostrar(alumnesOrdenats)
    hi_ha_expulsions_pendents_tramitar = True
    table2_expulsionsPendentsTramitar = Table2_ExpulsionsPendentsTramitar(
        expulsionsPendentsTramitar
    )
    hi_ha_expulsions_pendents_tramitar = len(expulsionsPendentsTramitar) > 0

    hi_ha_expulsions_daula = any(
        expulsio.es_expulsio_d_aula() for expulsio in expulsionsPendentsTramitar
    )

    if not hi_ha_expulsions_daula:
        table2_expulsionsPendentsTramitar.exclude = ("Assignatura",)

    hi_ha_expulsions_per_acumulacio = len(expulsionsPendentsPerAcumulacio) > 0

    table2_expulsionsPendentsPerAcumulacio = Table2_ExpulsionsPendentsPerAcumulacio(
        expulsionsPendentsPerAcumulacio
    )

    diccionariTables = dict()
    for tupla_alumne in alumnesOrdenats:
        expulsionsPerAlumne = tupla_alumne[1]["expulsions"]
        incidenciesPerAlumne = tupla_alumne[1]["incidencies"]
        expulsionsIIncidenciesPerAlumne = Table2_ExpulsionsIIncidenciesPerAlumne(
            expulsionsPerAlumne + incidenciesPerAlumne
        )
        expulsionsIIncidenciesPerAlumne.columns.hide(
            "Eliminar_Incidencia_Gestionada_Pel_Tutor"
        )

        diccionariTables[tupla_alumne[0] + " - " + unicode(tupla_alumne[1]["grup"])] = (
            expulsionsIIncidenciesPerAlumne
        )

    return render(
        request,
        "incidenciesProfessional.html",
        {
            "alumnes": alumnesOrdenats,
            "expulsionsPendentsTramitar": table2_expulsionsPendentsTramitar,
            "expulsionsPendentsTramitarBooelan": hi_ha_expulsions_pendents_tramitar,
            "expulsionsPendentsPerAcumulacioBooelan": hi_ha_expulsions_per_acumulacio,
            "expulsionsPendentsPerAcumulacio": table2_expulsionsPendentsPerAcumulacio,
            "expulsionsIIncidenciesPerAlumne": diccionariTables,
        },
    )


@login_required
@group_required(["direcció"])
def alertesAcumulacioExpulsions(request):
    (user, l4) = tools.getImpersonateUser(request)
    User2Professor(user)

    alumnesAmbExpulsions = (
        Expulsio.objects.filter(es_vigent=True)
        .exclude(estat="ES")
        .order_by("alumne__id")
        .values_list("alumne__id", flat=True)
    )

    alumnesAmbIncidenciesAula = (
        Incidencia.objects.filter(
            es_vigent=True,
            tipus__es_informativa=False,
            control_assistencia__isnull=False,
        )
        .order_by("alumne__id")
        .values_list("alumne__id", flat=True)
    )

    alumnesAmbIncidenciesForaAula = (
        Incidencia.objects.filter(
            es_vigent=True,
            tipus__es_informativa=False,
            control_assistencia__isnull=True,
        )
        .order_by("alumne__id")
        .values_list("alumne__id", flat=True)
    )

    tipus_incidencia = TipusIncidencia.objects.filter(es_informativa=False)
    alumnesAmbIncidenciesPerTipus = {}
    if settings.CUSTOM_TIPUS_INCIDENCIES:
        for t in tipus_incidencia:
            alumnesAmbIncidenciesPerTipus[t.id] = (
                Incidencia.objects.filter(
                    es_vigent=True, tipus__es_informativa=False, tipus__tipus=t
                )
                .order_by("alumne__id")
                .values_list("alumne__id", flat=True)
            )

    alumnesAmbExpulsions_dict = {}
    alumnesAmbIncidenciesAula_dict = {}
    alumnesAmbIncidenciesForaAula_dict = {}
    alumnesAmbIncidenciesPerTipus_dict = {}
    alumnes_ids = set()
    for x, g in groupby(alumnesAmbExpulsions, lambda x: x):
        alumnes_ids.add(x)
        alumnesAmbExpulsions_dict[x] = len(list(g))

    for x, g in groupby(alumnesAmbIncidenciesAula, lambda x: x):
        alumnes_ids.add(x)
        alumnesAmbIncidenciesAula_dict[x] = len(list(g))

    for x, g in groupby(alumnesAmbIncidenciesForaAula, lambda x: x):
        alumnes_ids.add(x)
        alumnesAmbIncidenciesForaAula_dict[x] = len(list(g))

    if settings.CUSTOM_TIPUS_INCIDENCIES:
        for t in tipus_incidencia:
            alumnesAmbIncidenciesPerTipus_dict[t.id] = {}
            for x, g in groupby(alumnesAmbIncidenciesPerTipus[t.id], lambda x: x):
                alumnes_ids.add(x)
                alumnesAmbIncidenciesPerTipus_dict[t.id][x] = len(list(g))

    alumnes = []
    for alumne in Alumne.objects.filter(id__in=alumnes_ids):
        alumne.nExpulsions = alumnesAmbExpulsions_dict.get(alumne.id, 0)
        alumne.nIncidenciesAula = alumnesAmbIncidenciesAula_dict.get(alumne.id, 0)
        alumne.nIncidenciesForaAula = alumnesAmbIncidenciesForaAula_dict.get(
            alumne.id, 0
        )
        alumne.nExpAndInc = (
            alumne.nExpulsions + alumne.nIncidenciesAula + alumne.nIncidenciesForaAula
        )

        alumne.nExpulsionsSort = alumne.nExpulsions * 10000 + (
            alumne.nIncidenciesAula + alumne.nIncidenciesForaAula
        )
        alumne.nIncidenciesAulaSort = (
            alumne.nIncidenciesAula * 10000
            + alumne.nExpulsions * 100
            + alumne.nIncidenciesForaAula
        )
        alumne.nIncidenciesForaAulaSort = (
            alumne.nIncidenciesForaAula * 10000
            + alumne.nExpulsions * 100
            + alumne.nIncidenciesAula
        )

        if settings.CUSTOM_TIPUS_INCIDENCIES:
            alumne.nIncidenciesPerTipus = {}
            alumne.nIncidenciesPerTipusSort = {}
            for t in tipus_incidencia:
                alumne.nIncidenciesPerTipus[t.id] = alumnesAmbIncidenciesPerTipus_dict[
                    t.id
                ].get(alumne.id, 0)
                setattr(alumne, str(t.id), alumne.nIncidenciesPerTipus[t.id])

        alumnes.append(alumne)

    # Envio les dades al table2
    if settings.CUSTOM_TIPUS_INCIDENCIES:
        import django_tables2 as tables

        attrs = dict(
            (
                str(t.id),
                tables.Column(verbose_name=t.tipus, order_by=str("-" + str(t.id))),
            )
            for t in tipus_incidencia
        )
        attrs["Meta"] = type(
            "Meta",
            (),
            {
                "attrs": {
                    "class": "paleblue table table-striped",
                },
                "sequence": [
                    "alumne",
                    "grup",
                    "expulsions",
                    "incidenciesAula",
                    "incidenciesForaAula",
                ]
                + [str(t.id) for t in tipus_incidencia]
                + ["expulsionsAndIncidencies", "sancionar"],
                "order_by": ("expulsions", "incidenciesAula", "incidenciesForaAula"),
                "template": "bootable2.html",
            },
        )

        table2 = type("DynamicTable", (Table2_AlertesAcumulacioExpulsions,), attrs)
    else:
        table2 = Table2_AlertesAcumulacioExpulsions

    table = table2(alumnes)

    RequestConfig(
        request, paginate={"paginator_class": DiggPaginator, "per_page": 50}
    ).configure(table)

    return render(
        request,
        "table2.html",
        {
            "table": table,
        },
    )


@login_required
@group_required(["direcció"])
def sancio(request, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    dia_prescriu_incidencia = date.today() - timedelta(
        days=settings.CUSTOM_DIES_PRESCRIU_INCIDENCIA
    )

    User2Professor(user)

    alumne = Alumne.objects.get(pk=pk)
    alumne.incidencia_set.filter(dia_incidencia__lte=dia_prescriu_incidencia).update(
        es_vigent=False
    )

    try:
        tipus = TipusSancio.objects.all()[0]
    except IndexError:
        tipus, _ = TipusSancio.objects.get_or_create(tipus="Expulsió del Centre")

    primeraFranja = FranjaHoraria.objects.all()[0]
    darreraFranja = FranjaHoraria.objects.reverse()[0]

    # expulsions:
    expulsions = alumne.expulsio_set.filter(es_vigent=True).exclude(estat="ES")

    str_expulsions = ", ".join(
        [
            e.motiu + " (" + unicode(e.dia_expulsio.strftime("%d/%m/%Y")) + ")"
            for e in expulsions
        ]
    )
    str_expulsions = (
        """Acumulació d'expulsions: {0}""".format(str_expulsions)
        if str_expulsions
        else ""
    )

    # incidències
    incidencies = alumne.incidencia_set.filter(
        tipus__es_informativa=False, es_vigent=True
    )

    str_incidencies = ", ".join(
        [
            i.descripcio_incidencia
            + " ("
            + unicode(i.dia_incidencia.strftime("%d/%m/%Y"))
            + ")"
            for i in incidencies
        ]
    )
    str_incidencies = (
        """Acumulació de incidències: {0}""".format(str_incidencies)
        if str_incidencies
        else ""
    )

    # expulsions + incidències
    comentaris_cap_d_estudis = " ".join([str_expulsions, str_incidencies])

    url_next = (
        "/incidencies/alertesAcumulacioExpulsions/"  # si res falla torno a la llista
    )
    try:
        sancio = Sancio(
            professor=User2Professor(user),
            alumne=alumne,
            tipus=tipus,
            motiu="",
            comentaris_cap_d_estudis=comentaris_cap_d_estudis,
            data_inici=datetime.today(),
            franja_inici=primeraFranja,
            franja_fi=darreraFranja,
            data_fi=datetime.today() + timedelta(days=1),
            data_carta=datetime.today(),
            signat="""Cap d'estudis""",
        )
        sancio.save()

        # LOGGING
        Accio.objects.create(
            tipus="EC",
            usuari=user,
            l4=l4,
            impersonated_from=request.user if request.user != user else None,
            text="""Creada sanció de l'alumne {0}.""".format(sancio.alumne),
        )

    except (ProfeNoPot, ValidationError) as e:
        resultat = {
            "errors": list(itertools.chain(*e.message_dict.values())),
            "warnings": [],
            "infos": [],
            "url_next": url_next,
        }
        return render(
            request,
            "resultat.html",
            {"head": "Error al crear sanció per acumulació.", "msgs": resultat},
        )
    else:
        # assigno les expulsions a aquesta sancio
        expulsions.update(es_vigent=False, provoca_sancio=sancio)

        # assigno les incidències a aquesta sancio
        if incidencies.count() > 0:
            incidencies.update(es_vigent=False, provoca_sancio=sancio)

        url_next = "/incidencies/editaSancio/{0}".format(sancio.pk)

    return HttpResponseRedirect(url_next)


# --------------------------------------------------------------------------------------------------


@login_required
@group_required(["direcció"])
def sancions(request, s="nom"):
    report = []

    ordenacions = {
        "nom": [
            "alumne__cognoms",
            "data_inici",
        ],
        "data": [
            "data_inici",
            "alumne__cognoms",
        ],
    }
    ordenacio = ordenacions[s] if s in ordenacions else []
    taula = tools.classebuida()

    taula.titol = tools.classebuida()
    taula.titol.contingut = "Sancions"
    taula.capceleres = []

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = "Alumne"
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 7
    capcelera.contingut = "Tipus"
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 5
    capcelera.contingut = "Obre Expedient"
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = "Periode sanció"
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 9
    capcelera.contingut = "Data Carta"
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 9
    capcelera.contingut = "Expulsions Relacionades"
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 45
    capcelera.contingut = "Incidències Relacionades"
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 5
    capcelera.contingut = "Accions"
    taula.capceleres.append(capcelera)

    taula.fileres = []

    sancions = Sancio.objects.order_by(*ordenacio)

    for sancio in sancions:
        filera = []

        # -nom--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = ""
        camp.contingut = (
            unicode(sancio.alumne) + " (" + unicode(sancio.alumne.grup) + ")"
        )
        filera.append(camp)

        # -tipus-----------------------------------------------------
        camp = tools.classebuida()
        camp.enllac = ""
        camp.contingut = unicode(sancio.tipus)
        filera.append(camp)

        # -obre expedient--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = ""
        camp.contingut = "Sí" if sancio.obra_expedient else "No"
        filera.append(camp)

        # -periode--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = "{0} a {1}".format(
            sancio.data_inici.strftime("%d/%m/%Y"), sancio.data_fi.strftime("%d/%m/%Y")
        )
        filera.append(camp)

        # -data carta--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = "{0}{1}".format(
            sancio.data_carta.strftime("%d/%m/%Y") if sancio.data_carta else "",
            " (impresa)" if sancio.impres else "",
        )

        filera.append(camp)

        # -Expulsions relacionades--------------------------------------------
        camp = tools.classebuida()
        camp.multipleContingut = [
            (
                e.dia_expulsio.strftime("%d/%m/%Y"),
                "/incidencies/editaExpulsio/{0}".format(e.pk),
            )
            for e in sancio.expulsio_set.exclude(estat="ES")
        ]
        filera.append(camp)

        # -Incidencies relacionades--------------------------------------------
        camp = tools.classebuida()
        camp.multipleContingut = [
            (
                "{0} ({1})".format(
                    i.dia_incidencia.strftime("%d/%m/%Y"), i.descripcio_incidencia
                ),
                "",
            )
            for i in sancio.incidencia_set.all()
        ]
        filera.append(camp)

        # -Incidencies relacionades--------------------------------------------
        camp = tools.classebuida()
        camp.esMenu = True
        camp.multipleContingut = [
            ("Editar", "/incidencies/editaSancio/{0}".format(sancio.pk)),
            (
                "Carta",
                "/incidencies/cartaSancio/{0}".format(sancio.pk),
            ),
            (
                "Esborrar",
                r"""javascript:confirmAction("/incidencies/esborrarSancio/{0}", "Segur que vols esborrar la sanció de {1}?")""".format(
                    sancio.pk, sancio.alumne
                ),
            ),
        ]
        filera.append(camp)

        taula.fileres.append(filera)

    report.append(taula)

    return render(
        request,
        "sancions.html",
        {
            "report": report,
            "head": "Informació Sancions",
        },
    )


@login_required
@group_required(["direcció"])
def sancionsExcel(request):
    """
    Generates an Excel spreadsheet for review by a staff member.
    """
    sancions = Sancio.objects.order_by("data_inici", "alumne__cognoms")

    dades_sancions = [
        [
            e.alumne,
            e.tipus,
            e.data_inici.strftime("%d/%m/%Y"),
            e.data_fi.strftime("%d/%m/%Y"),
            "Sí" if e.impres else "No",
            e.alumne.grup.descripcio_grup,
            e.alumne.grup.curs.nivell,
        ]
        for e in sancions
    ]

    capcelera = [
        "Alumne",
        "Tipus",
        "Data inici",
        "Data fi",
        "Ha estat imprés",
        "grup",
        "nivell",
    ]

    template = loader.get_template("export.csv")
    context = {
        "capcelera": capcelera,
        "dades": dades_sancions,
    }

    response = HttpResponse()
    filename = "sancions.csv"

    response["Content-Disposition"] = "attachment; filename=" + filename
    response["Content-Type"] = "text/csv; charset=utf-8"
    # response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    # Add UTF-8 'BOM' signature, otherwise Excel will assume the CSV file
    # encoding is ANSI and special characters will be mangled
    response.write("\xef\xbb\xbf")
    response.write(template.render(context))

    return response


@login_required
@group_required(["direcció"])
def cartaSancio(request, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    sancio = Sancio.objects.get(pk=pk)
    nom_fitxer = "cartaSancio-" + sancio.tipus.carta_slug

    # seg---------
    pot_entrar = True or l4 or sancio.professor.pk == user.pk
    if not pot_entrar:
        raise Http404()

    sancio.credentials = credentials

    # capcelera
    report = tools.classebuida()
    report.nom_alumne = unicode(sancio.alumne)
    report.grup_alumne = unicode(sancio.alumne.grup.descripcio_grup)
    # deprecated: cal evitar dies_expulsio i utilitzar dia_inicial i dia_final
    report.dies_expulsio = " del {0} al {1}".format(
        sancio.data_inici.strftime("%d/%m/%Y"),
        sancio.data_fi.strftime("%d/%m/%Y"),
    )
    report.dia_inicial = sancio.data_inici.strftime("%d/%m/%Y")
    report.dia_final = sancio.data_fi.strftime("%d/%m/%Y")
    report.hora_inicial = sancio.franja_inici.hora_inici.strftime("%H:%M")
    report.hora_final = sancio.franja_fi.hora_fi.strftime("%H:%M")

    capDeSetmana = DiaDeLaSetmana.objects.filter(es_festiu=True).values_list(
        "n_dia_ca", flat=True
    )
    generadorDies = (
        sancio.data_inici + timedelta(d)
        for d in range((sancio.data_fi - sancio.data_inici).days + 1)
    )
    report.quantitat_dies = sum(
        1 for dia in generadorDies if dia.weekday() not in capDeSetmana
    )

    report.motiu = sancio.motiu
    report.signat_per = sancio.signat
    report.data_signatura = sancio.data_carta.strftime("%d/%m/%Y")
    report.expulsions = []
    report.incidencies = []
    # detall
    for e in sancio.expulsio_set.exclude(estat="ES"):
        rpt_e = tools.classebuida()
        rpt_e.dia = e.dia_expulsio.strftime("%d/%m/%Y")
        rpt_e.professor = "Sr/a: {0}".format(e.professor)
        rpt_e.comunicacio = (
            "{0} - {1}".format(
                e.moment_comunicacio_a_tutors.strftime("%d/%m/%Y"),
                e.tutor_contactat_per_l_expulsio,
            )
            if e.moment_comunicacio_a_tutors
            else ""
        )
        rpt_e.motiu = e.motiu
        report.expulsions.append(rpt_e)

    for i in sancio.incidencia_set.all():
        rpt_i = tools.classebuida()
        rpt_i.data = i.dia_incidencia.strftime("%d/%m/%Y")
        rpt_i.professor = "Sr/a: {0}".format(i.professional)
        assignatura = """'(fora d'aula')"""
        try:
            assignatura = i.control_assistencia.impartir.horari.assignatura
        except:  # noqa: E722
            pass
        rpt_i.assignatura = "{0}".format(assignatura)
        rpt_i.tipus = i.tipus
        rpt_i.descripcio = i.descripcio_incidencia
        report.incidencies.append(rpt_i)

    # from django.template import Context
    import html
    import os
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
        path = os.path.join(
            settings.PROJECT_DIR, "../customising/docs/" + nom_fitxer + ".odt"
        )
        if not os.path.isfile(path):
            path = os.path.join(
                os.path.dirname(__file__), "templates/" + nom_fitxer + ".odt"
            )

        renderer = Renderer(
            path,
            {
                "report": report,
            },
            resultat,
        )
        renderer.run()
        docFile = open(resultat, "rb")
        contingut = docFile.read()
        docFile.close()
        os.remove(resultat)

    except Exception as e:
        excepcio = unicode(e)

    if not excepcio:
        sancio.impres = True
        sancio.save()
        response = http.HttpResponse(
            contingut, content_type="application/vnd.oasis.opendocument.text"
        )
        response["Content-Disposition"] = 'attachment; filename="{0}-{1}.odt"'.format(
            nom_fitxer, slugify(unicode(sancio.alumne))
        )

    else:
        response = http.HttpResponse(
            """Als Gremlin no els ha agradat aquest fitxer! %s"""
            % html.escape(excepcio)
        )

    return response


@login_required
@group_required(["direcció"])
def editaSancio(request, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    sancio = Sancio.objects.get(pk=pk)

    # seg---------
    pot_entrar = l4 or user.groups.filter(name="direcció").exists()
    if not pot_entrar:
        raise Http404()

    sancio.credentials = credentials

    edatAlumne = None
    try:
        edatAlumne = sancio.alumne.edat()
    except:  # noqa: E722
        pass

    resps = sancio.alumne.get_dades_responsables()

    infoForm = [
        ("Alumne", unicode(sancio.alumne)),
        ("Edat alumne", edatAlumne),
        ("Responsable preferent", resps["respPre"]),
        ("Responsable (altre)", resps["respAlt"]),
        ("Altres telèfons", sancio.alumne.get_telefons()),
        ("Carta impresa (sanció bloquejada)", sancio.impres),
    ]

    fields = [
        "tipus",
        "data_inici",
        "franja_inici",
        "data_fi",
        "franja_fi",
        "data_carta",
        "motiu",
        "obra_expedient",
        "comentaris_cap_d_estudis",
        "signat",
    ]
    if l4:
        fields.extend(["professor", "impres"])

    editaSancioFormF = modelform_factory(Sancio, fields=fields)
    try:
        editaSancioFormF.base_fields["data_inici"].widget = DateTextImput()
        editaSancioFormF.base_fields["data_fi"].widget = DateTextImput()
        editaSancioFormF.base_fields["data_carta"].widget = DateTextImput()
    except:  # noqa: E722
        pass

    if request.method == "POST":
        formSancio = editaSancioFormF(data=request.POST, instance=sancio)
        can_delete = ckbxForm(
            data=request.POST,
            label="Esborrar sanció",
            help_text="""Marca aquesta cassella per esborrar aquesta sanció""",
        )
        formSelectIncidencies = incidenciesRelacionadesForm(
            data=request.POST,
            querysetIncidencies=sancio.incidencia_set.all(),
            querysetExpulsions=sancio.expulsio_set.all(),
        )

        try:
            if (
                formSancio.is_valid()
                and can_delete.is_valid()
                and formSelectIncidencies.is_valid()
            ):
                if can_delete.cleaned_data["ckbx"] and l4:
                    sancio.delete()
                else:
                    formSancio.save()

                    dia_prescriu_incidencia = date.today() - timedelta(
                        days=settings.CUSTOM_DIES_PRESCRIU_INCIDENCIA
                    )
                    dia_prescriu_expulsio = date.today() - timedelta(
                        days=settings.CUSTOM_DIES_PRESCRIU_EXPULSIO
                    )

                    incidencies = formSelectIncidencies.cleaned_data[
                        "incidenciesRelacionades"
                    ]
                    incidencies_a_desvincular = sancio.incidencia_set.exclude(
                        pk__in=[i.pk for i in incidencies]
                    )
                    incidencies_a_desvincular.filter(
                        dia_incidencia__gte=dia_prescriu_incidencia
                    ).update(es_vigent=True)
                    incidencies_a_desvincular.update(provoca_sancio=None)

                    expulsions = formSelectIncidencies.cleaned_data[
                        "expulsionsRelacionades"
                    ]
                    expulsions_a_desvincular = sancio.expulsio_set.exclude(
                        pk__in=[i.pk for i in expulsions]
                    )
                    expulsions_a_desvincular.filter(
                        dia_expulsio__gte=dia_prescriu_expulsio
                    ).update(es_vigent=True)
                    expulsions_a_desvincular.update(provoca_sancio=None)

                url = "/incidencies/sancions/"
                return HttpResponseRedirect(url)
        except ValueError as e:
            msg = "S'ha produit un error intern. Potser que hagis sortit de mode L4 a mig procés?. L'error intern és {}".format(
                str(e)
            )
            formSancio.add_error(
                field=None, error=msg
            )  # rebo errors perquè penso que es barreja mode L4 i no L4

    else:
        formSancio = editaSancioFormF(instance=sancio)
        can_delete = ckbxForm(
            data=request.POST,
            label="Esborrar sanció:",
            help_text="""Marca aquesta cassella per esborrar aquesta sanció""",
        )
        formSelectIncidencies = incidenciesRelacionadesForm(
            querysetIncidencies=sancio.incidencia_set.order_by("dia_incidencia").all(),
            querysetExpulsions=sancio.expulsio_set.order_by("dia_expulsio").all(),
        )

    formSancio.infoForm = infoForm
    formset = [formSancio, formSelectIncidencies]
    formset.extend([can_delete] if l4 else [])

    return render(
        request,
        "formset.html",
        {
            "formset": formset,
            "infoForm": infoForm,
            "head": "Sanció",
        },
    )


# --------------------------------------------------------------------------------------------------


login_required


@group_required(["direcció"])
def esborrarSancio(request, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    sancio = Sancio.objects.get(pk=pk)

    # seg---------
    pot_entrar = l4 or user.groups.filter(name="direcció").exists()
    if not pot_entrar:
        raise Http404()

    if not l4 and sancio.impres:
        return render(
            request,
            "resultat.html",
            {
                "head": "Error esborrant sanció",
                "msgs": {
                    "errors": [
                        "Aquesta sanció ja ha estat impresa, no es pot esborrar"
                    ],
                    "warnings": [],
                    "infos": [],
                    "url_next": "/incidencies/sancions/",
                },
            },
        )

    sancio.credentials = credentials

    try:
        # esborrar totes les expulsions i incidències relacionades:
        _ = (
            apps.get_model("incidencies", "Expulsio")
            .objects.filter(provoca_sancio=sancio)
            .update(provoca_sancio=None, es_vigent=True)
        )
        _ = (
            apps.get_model("incidencies", "Incidencia")
            .objects.filter(provoca_sancio=sancio)
            .update(provoca_sancio=None, es_vigent=True)
        )

        # preescriure incidències
        preescriu()

        # esborrar-la
        sancio.delete()

    except (ProfeNoPot, ValidationError) as e:
        # Com que no és un formulari de model cal tractar a mà les incidències del save:
        for _, v in e.message_dict.items():
            for x in v:
                messages.error(request, x)
    except ProtectedError:
        messages.error(request, "Aquesta sanció té expulsions relacionades.")

    url = "/incidencies/sancions/"
    return HttpResponseRedirect(url)


@login_required
@group_required(["direcció"])
def controlTramitacioExpulsions(request):
    (user, l4) = tools.getImpersonateUser(request)
    User2Professor(user)

    expulsions = Expulsio.objects.exclude(estat="ES").exclude(
        moment_comunicacio_a_tutors__isnull=False
    )

    table = Table2_ExpulsioTramitar(list(expulsions))
    table.order_by = "total_expulsions_vigents"

    RequestConfig(
        request, paginate={"paginator_class": DiggPaginator, "per_page": 10}
    ).configure(table)

    return render(
        request,
        "table2.html",
        {
            "table": table,
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


# ------No esborrar: com afegir errors a mà en un formulari a partir dels ValidationsError:
#                try:
#                    incidencia.save()
#                    Incidencia_despres_de_posar( incidencia )
#                    url = '/incidencies/llistaIncidenciesProfessional'  #todo: a la pantalla d''incidencies
#                    return HttpResponseRedirect( url )
#                except ValidationError, e:
#                    #Com que no és un formulari de model cal tractar a mà les incidències del save:
#                    for _, v in e.message_dict.items():
#                        formIncidencia._errors.setdefault(NON_FIELD_ERRORS, []).extend(  v  )
