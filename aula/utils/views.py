# This Python file uses the following encoding: utf-8

# templates
from django.http.response import HttpResponse, JsonResponse, Http404
from django.template import RequestContext
from django.shortcuts import render
from aula.apps.extKronowin.models import ParametreKronowin
from django.contrib.auth.hashers import check_password

from django.http import HttpResponseRedirect
from django.contrib.auth import logout

from django.contrib.auth.models import Group

# auth
from django.contrib.auth.decorators import login_required

from aula.settings import CUSTOM_SORTIDES_PAGAMENT_ONLINE
from aula.settings import CUSTOM_GRUPS_PODEN_VEURE_FOTOS
from aula.utils.decorators import group_required
from aula.utils import tools
from aula.apps.usuaris.models import User2Professor
from aula.apps.presencia.models import Impartir
from datetime import datetime
from datetime import timedelta
from django.db.models import Q

from django.conf import settings
from django.urls import reverse

from aula.utils.tools import (
    calculate_my_time_off,
    processInitComplet,
    executaAmbOSenseThread,
)
from aula.utils.forms import initDBForm

from django.views.decorators.csrf import ensure_csrf_cookie
from aula.apps.alumnes.models import Curs


def keepalive(request):
    if request.user.is_authenticated:
        my_timeoff = calculate_my_time_off(request.user)
        return JsonResponse(
            {
                "my_timeoff": my_timeoff,
                "my_safe_timeoff": my_timeoff - 10,
                "Im_authenticate": True,
            }
        )
    else:
        return JsonResponse(
            {
                "timeout": 0,
                "safetimeout": 0,
                "authenticate": False,
            }
        )


def logout_page(request):
    try:
        del request.session["impersonacio"]
    except KeyError:
        pass

    logout(request)
    return HttpResponseRedirect("/")


@ensure_csrf_cookie
def menu(request):
    # How do I make a variable available to all my templates?
    # http://readthedocs.org/docs/django/1.2.4/faq/usage.html#how-do-i-make-a-variable-available-to-all-my-templates

    if request.user.is_anonymous:
        return HttpResponseRedirect(settings.LOGIN_URL)
    else:
        # si és un alumne l'envio a mirar el seu informe
        try:
            if Group.objects.get(name="alumne") in request.user.groups.all():
                return HttpResponseRedirect("/open/elMeuInforme/")

            # comprova que no té passwd per defecte:
            defaultPasswd, _ = ParametreKronowin.objects.get_or_create(
                nom_parametre="passwd", defaults={"valor_parametre": "1234"}
            )
            if check_password(defaultPasswd.valor_parametre, request.user.password):
                return HttpResponseRedirect(reverse("usuari__dades__canvi_passwd"))

            # si no té les dades informades:
            if not request.user.first_name or not request.user.last_name:
                return HttpResponseRedirect("/usuaris/canviDadesUsuari/")

        except:
            pass

        # prenc impersonate user:
        (user, _) = tools.getImpersonateUser(request)

        # si és professor ves a mostra impartir:
        professor = User2Professor(user)
        if professor is not None:
            return HttpResponseRedirect("/presencia/mostraImpartir/")

    return render(
        request,
        "main_page.html",
        {},
    )


@login_required
@group_required(["direcció"])
def carregaInicial(request):

    return render(
        request,
        "carregaInicial.html",
        {},
    )


@login_required
def about(request):
    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    professor = User2Professor(user)

    report = []
    taula = tools.classebuida()

    taula.titol = tools.classebuida()
    taula.titol.contingut = ""
    taula.titol.enllac = None

    taula.capceleres = []

    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = "Informació"
    capcelera.enllac = None
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 80
    capcelera.contingut = ""
    taula.capceleres.append(capcelera)

    taula.fileres = []

    filera = []

    # -by--------------------------------------------
    camp = tools.classebuida()
    camp.enllac = None
    camp.contingut = "Llicència"
    camp.enllac = ""
    filera.append(camp)

    # -tip--------------------------------------------

    licenseFile = open(settings.LICENSE_FILE, "r")
    tip = licenseFile.read()

    camp = tools.classebuida()
    camp.enllac = ""
    camp.contingut = tip
    filera.append(camp)

    taula.fileres.append(filera)

    # -1--------------------------------------------
    filera = []

    camp = tools.classebuida()
    camp.enllac = None
    camp.contingut = "Codi"
    camp.enllac = ""
    filera.append(camp)

    # -tip--------------------------------------------

    tip = """Pots revisar aquí el codi i les actualitzacions del programa.
    """
    camp = tools.classebuida()
    camp.enllac = r"https://github.com/ctrl-alt-d/django-aula"
    camp.contingut = tip
    filera.append(camp)

    taula.fileres.append(filera)

    report.append(taula)

    # --Estadistiques Professor.....................
    if professor:
        taula = tools.classebuida()

        taula.titol = tools.classebuida()
        taula.titol.contingut = ""
        taula.titol.enllac = None

        taula.capceleres = []

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = "Estadístiques"
        capcelera.enllac = None
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 80
        capcelera.contingut = ""
        taula.capceleres.append(capcelera)

        taula.fileres = []

        filera = []

        camp = tools.classebuida()
        camp.contingut = "Percentatge de passar llista a les teves imparticions:"
        filera.append(camp)

        camp = tools.classebuida()
        camp.enllac = None
        qProfessor = Q(horari__professor=professor)

        qAvui = Q(dia_impartir=datetime.today()) & Q(
            horari__hora__hora_fi__lt=datetime.now()
        )
        qFinsAhir = Q(dia_impartir__lt=datetime.today())
        qFinsAra = qFinsAhir | qAvui
        qTeGrup = Q(horari__grup__isnull=False)
        imparticions = Impartir.objects.filter(qProfessor & qFinsAra & qTeGrup)
        nImparticionsLlistaPassada = (
            imparticions.filter(professor_passa_llista__isnull=False)
            .order_by()
            .distinct()
            .count()
        )
        nImparticionsLlistaPendent = (
            imparticions.filter(professor_passa_llista__isnull=True)
            .order_by()
            .distinct()
            .count()
        )
        nImparticios = nImparticionsLlistaPassada + nImparticionsLlistaPendent

        pct = (
            "{0:.0f}".format(nImparticionsLlistaPassada * 100 / nImparticios)
            if nImparticios > 0
            else "N/A"
        )
        estadistica1 = "{0}% ({1} classes impartides, {2} controls)".format(
            pct, nImparticios, nImparticionsLlistaPassada
        )

        # ---hores de classe
        nProfessor = Impartir.objects.filter(
            horari__professor=professor, horari__grup__isnull=False
        ).count()
        nTotal = Impartir.objects.filter(horari__grup__isnull=False).count()
        estadistica2 = f"Aquest curs impartirem {nTotal:,} hores de classe; d'aquestes, {nProfessor:,} les imparteixes tu."

        camp.contingut = "{0}. {1}".format(estadistica1, estadistica2)
        filera.append(camp)

        taula.fileres.append(filera)

        report.append(taula)

    return render(
        request,
        "report.html",
        {
            "report": report,
            "head": "About",
        },
    )


@login_required
@group_required(["professors"])
def estadistiques(request):
    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    professor = User2Professor(user)
    report = []

    # --Estadistiques Professor.....................
    if professor:
        taula = tools.classebuida()
        taula.titol = tools.classebuida()
        taula.titol.contingut = ""
        taula.titol.enllac = None
        taula.capceleres = []
        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = "Estadístiques"
        capcelera.enllac = None
        taula.capceleres.append(capcelera)
        capcelera = tools.classebuida()
        capcelera.amplade = 80
        capcelera.contingut = ""
        taula.capceleres.append(capcelera)
        taula.fileres = []
        filera = []
        camp = tools.classebuida()
        camp.contingut = "Percentatge de passar llista a les teves imparticions:"
        filera.append(camp)
        camp = tools.classebuida()
        camp.enllac = None
        qProfessor = Q(horari__professor=professor)
        qFinsAra = Q(dia_impartir__lt=datetime.today())
        qTeGrup = Q(horari__grup__isnull=False)
        imparticions = Impartir.objects.filter(qProfessor & qFinsAra & qTeGrup)
        qSenseAlumnes = Q(controlassistencia__isnull=True)
        qProfeHaPassatLlista = Q(professor_passa_llista__isnull=False)
        nImparticionsLlistaPassada = (
            imparticions.filter(qProfeHaPassatLlista | qSenseAlumnes)
            .order_by()
            .distinct()
            .count()
        )
        nImparticionsLlistaPendent = (
            imparticions.filter(professor_passa_llista__isnull=True)
            .exclude(controlassistencia__isnull=True)
            .order_by()
            .distinct()
            .count()
        )
        nImparticios = nImparticionsLlistaPassada + nImparticionsLlistaPendent
        pct = (
            "{0:.1f}".format(nImparticionsLlistaPassada * 100 / nImparticios)
            if nImparticios > 0
            else "N/A"
        )
        estadistica1 = (
            "{0}% ({1} classes impartides, {2} controls, falten {3} controls)".format(
                pct,
                nImparticios,
                nImparticionsLlistaPassada,
                nImparticionsLlistaPendent,
            )
        )

        # ---hores de classe
        nProfessor = Impartir.objects.filter(
            horari__professor=professor, horari__grup__isnull=False
        ).count()
        nTotal = Impartir.objects.filter(horari__grup__isnull=False).count()
        estadistica2 = f"Aquest curs impartirem {nTotal:,} hores de classe; d'aquestes, {nProfessor:,} les imparteixes tu."

        camp.contingut = "{0}. {1}".format(estadistica1, estadistica2)
        filera.append(camp)

        taula.fileres.append(filera)

        report.append(taula)

        taula = tools.classebuida()

        taula.titol = tools.classebuida()
        taula.titol.contingut = ""
        taula.titol.enllac = None

        taula.capceleres = []

        capcelera = tools.classebuida()
        capcelera.amplade = 100
        capcelera.contingut = "Imparticions pendents passar llista"
        capcelera.enllac = None
        taula.capceleres.append(capcelera)

        taula.fileres = []

        for imparticio in imparticions.filter(
            professor_passa_llista__isnull=True
        ).exclude(controlassistencia__isnull=True):
            filera = []
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = "/presencia/passaLlista/{0}".format(imparticio.pk)
            camp.contingut = "{0} - {1}".format(
                imparticio.dia_impartir, imparticio.horari
            )
            camp.negreta = True
            filera.append(camp)
            taula.fileres.append(filera)

        report.append(taula)

    return render(
        request,
        "report.html",
        {
            "report": report,
            "head": "Estadistiques",
        },
    )


@login_required
def pagamentOnLine(request):

    if (
        not settings.CUSTOM_SORTIDES_PAGAMENT_ONLINE
        and not settings.CUSTOM_QUOTES_ACTIVES
    ):
        raise Http404()

    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    report = []
    taula = tools.classebuida()

    taula.titol = tools.classebuida()
    taula.titol.contingut = ""
    taula.titol.enllac = None

    taula.capceleres = []

    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = "Informació"
    capcelera.enllac = None
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 80
    capcelera.contingut = ""
    taula.capceleres.append(capcelera)

    taula.fileres = []

    filera = []

    # -by--------------------------------------------
    camp = tools.classebuida()
    camp.enllac = None
    camp.contingut = "Dades Fiscals"
    camp.enllac = ""
    filera.append(camp)

    # -tip--------------------------------------------

    dadesFiscalsFile = open(settings.DADES_FISCALS_FILE, "r")
    tip = dadesFiscalsFile.read()

    camp = tools.classebuida()
    camp.enllac = ""
    camp.contingut = tip
    filera.append(camp)

    taula.fileres.append(filera)

    # -1--------------------------------------------
    filera = []

    camp = tools.classebuida()
    camp.enllac = None
    camp.contingut = "Política de vendes/devolucions"
    camp.enllac = ""
    filera.append(camp)

    # -tip--------------------------------------------

    politicaVendesFile = open(settings.POLITICA_VENDA_FILE, "r")
    tip = politicaVendesFile.read()

    camp = tools.classebuida()
    camp.enllac = ""
    camp.contingut = tip
    filera.append(camp)

    taula.fileres.append(filera)

    if hasattr(settings, "POLITICA_COOKIES") and bool(settings.POLITICA_COOKIES):
        # -1--------------------------------------------
        filera = []

        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = "Política de cookies"
        camp.enllac = ""
        filera.append(camp)

        # -tip--------------------------------------------

        try:
            politicaCookies = open(settings.POLITICA_COOKIES, "r")
            tip = politicaCookies.read()
        except:
            tip = "Fitxer " + settings.POLITICA_COOKIES + " no disponible"
        camp = tools.classebuida()
        camp.enllac = ""
        camp.contingut = tip
        filera.append(camp)

        taula.fileres.append(filera)

    if hasattr(settings, "POLITICA_RGPD") and bool(settings.POLITICA_RGPD):
        # -1--------------------------------------------
        filera = []

        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = "Protecció de dades de caràcter personal"
        camp.enllac = ""
        filera.append(camp)

        # -tip--------------------------------------------

        try:
            politicaDadesPer = open(settings.POLITICA_RGPD, "r")
            tip = politicaDadesPer.read()
        except:
            tip = "Fitxer " + settings.POLITICA_RGPD + " no disponible"
        camp = tools.classebuida()
        camp.enllac = ""
        camp.contingut = tip
        filera.append(camp)

        taula.fileres.append(filera)

    report.append(taula)

    return render(
        request,
        "report.html",
        {
            "report": report,
            "head": "Pagament Online",
        },
    )


@login_required
def calendariDevelop(request):
    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    return render(
        request,
        "calendariDevelop.html",
        {
            "head": "Calendari desenvolupament.",
        },
    )


def blanc(request):
    return render(
        request,
        "blanc.html",
        {},
    )


def allow_private_files(private_file):
    from aula.apps.alumnes.models import Alumne
    from aula.apps.matricula.models import Document

    request = private_file.request
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    if not request.user.is_authenticated:
        return False

    if private_file.relative_name.startswith("matricula"):
        data = Document.objects.filter(
            matricula__alumne__user_associat=user, fitxer=private_file.relative_name
        )
        if data:
            return request.user.is_authenticated

    prop = Alumne.objects.filter(user_associat=user, foto=private_file.relative_name)
    if prop:
        return request.user.is_authenticated

    pertany_al_grup_permes = user.groups.filter(
        name__in=CUSTOM_GRUPS_PODEN_VEURE_FOTOS
    ).exists()
    return request.user.is_authenticated and pertany_al_grup_permes


@login_required
@group_required(["administradors"])
def initDB(request):

    head = "Inicialitza base de dades per començar nou curs"

    if request.method == "POST":
        form = initDBForm(request.POST)
        if form.is_valid():

            data_fi = Curs.objects.exclude(data_fi_curs__isnull=True).order_by(
                "-data_fi_curs"
            )
            if data_fi.exists():
                data_fi = data_fi[0].data_fi_curs
            else:
                data_fi = None

            if data_fi is None or data_fi + timedelta(days=30) < datetime.now().date():
                # Ha passat un mes des del final de curs o no n'hi ha cap data de final de curs
                r = processInitComplet(user=request.user)
                executaAmbOSenseThread(r)

                errors = []
                warnings = []
                infos = ["Iniciat procés d'inicialització"]
            else:
                # Encara no ha passat un mes des de final de curs
                errors = []
                warnings = []
                infos = [
                    "No es pot fer la inicialització fins un mes després del final de curs"
                ]

            resultat = {"errors": errors, "warnings": warnings, "infos": infos}
            return render(
                request,
                "resultat.html",
                {"head": head, "msgs": resultat},
            )
    else:
        form = initDBForm()
    return render(
        request,
        "form.html",
        {"form": form, "head": head},
    )
