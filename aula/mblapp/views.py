# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals

from django.contrib.humanize.templatetags.humanize import naturalday
from django.http import HttpResponseServerError
from django.shortcuts import render, get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from aula.apps.alumnes.models import Alumne
from aula.apps.missatgeria.missatges_a_usuaris import tipusMissatge, ERROR_REALITZANT_PAGAMENT_ONLINE_MOBIL
from aula.apps.sortides.views import logPagaments
from aula.mblapp.security_rest import EsUsuariDeLaAPI
import uuid
from rest_framework.parsers import JSONParser
from aula.apps.usuaris.models import QRPortal
from aula.mblapp.serializers import QRTokenSerializer, DarreraSincronitzacioSerializer, PagamentRealitzatSerializer
from django.contrib.auth.models import User, Group
from django.utils.crypto import get_random_string
from django.db import transaction
from rest_framework import serializers
from django.conf import settings
from datetime import datetime
from datetime import timedelta
from aula.apps.presencia.models import EstatControlAssistencia
from aula.apps.presencia.models import ControlAssistencia
from aula.apps.avaluacioQualitativa.models import AvaluacioQualitativa
from aula.apps.sortides.models import NotificaSortida, Sortida, SortidaPagament, Pagament
from aula.utils.tools import unicode

# ----------- vistes per a testos --------------------------------

@api_view(['GET'])
@permission_classes((AllowAny, ))
def hello_api(request, format=None):
    content = {
        'status': 'here we are'
    }
    return Response(content)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def hello_api_login(request, format=None):
    content = {
        'status': 'here we are just login'
    }
    return Response(content)


@api_view(['GET'])
@permission_classes((EsUsuariDeLaAPI,))
def hello_api_login_app(request, format=None):
    content = {
        'status': 'here we are login group app'
    }
    return Response(content)


# ---------------------  user x token ----------------------------
# La vista que genera el QR és a l'App portal famílies.

# ----------------------------------------------------------------

#@csrf_exempt
@transaction.atomic
@api_view(['POST'])
@permission_classes((AllowAny, ))
def capture_token_api(request, format=None):
    """
    Rep un token i retorna un usuari de la API (is_active=False)
    """
    import secrets

    # deserialitzem
    data = JSONParser().parse(request)
    serializer = QRTokenSerializer(data=data)
    if not serializer.is_valid():
        raise serializers.ValidationError({"error": ["ups! Aquest token no serveix"]})
    # busquem el token
    key = serializer.validated_data["key"]
    born_date = serializer.validated_data["born_date"]
    token = (QRPortal
             .objects
             .filter( moment_captura__isnull = True, clau = key )
             .first()
            )

    if "validacions del token":

        # si no hi ha token -> error
        if not token:
            raise serializers.ValidationError({'error': ["ups! Aquest QR no serveix. Potser ja l'has utilitzat abans?"]})

        # si el token ja ha estat previament capturat
        if token.moment_captura:
            raise serializers.ValidationError({'error': ["ups! Aquest QR no serveix. Potser ja l'has utilitzat abans?"]})

        # caducat?
        caduca_dia = token.moment_expedicio + timedelta(days=settings.CUSTOM_DIES_API_TOKEN_VALID)
        if datetime.now() > caduca_dia:
            raise serializers.ValidationError({'error': ["ups! Aquest token ja ha caducat"]})
        # born date is ok?
        fuky_random_jesucryst_date = datetime(1000,1,1).date
        db_born_date = ( token.alumne_referenciat.data_neixement or fuky_random_jesucryst_date )
        if db_born_date != born_date:
            raise serializers.ValidationError({'error': ["Data de naixement no vàlida"]})

    # creo un nou usuari per aquest token
    allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789' +  '0Oo^?#!'
    password_xunga = ''.join(secrets.choice(allowed_chars) for i in range(12))
    nou_usuari = User.objects.create_user( username = "API"+token.localitzador ,
                                           email = "",
                                           password = password_xunga )
    grup_api, _ = Group.objects.get_or_create(name='API')
    nou_usuari.groups.add(grup_api)
    nou_usuari.is_active = False             #serà actiu quan el tutor l'activi
    nou_usuari.save()

    # assigno usuari al token
    token.moment_captura = datetime.now()
    token.usuari_referenciat = nou_usuari
    ara = datetime.now()
    token.novetats_detectades_moment= ara
    token.save()

    # preparem resposta
    content = {
        'username': nou_usuari.username,
        'password': password_xunga,
    }

    return Response(content)


@api_view(['GET'])
@permission_classes((EsUsuariDeLaAPI,))
def notificacions_mes(request, mes, format=None):
    """
    Rep el mes i retorna tots valors actuals.
    """
    #ara = datetime.now()
    #data = JSONParser().parse(request)
    #serializer = DarreraSincronitzacioSerializer(data=data)
    #if not serializer.is_valid():
    #    raise serializers.ValidationError("ups! petició amb errors")

    qrtoken = request.user.qrportal

    if int(mes)<1 or int(mes)>12:
        raise serializers.ValidationError({'error': ["Mes inexistent"]})
    # Tant si hi ha novetats com si no s'envia tota la info del mes:

    alumne = qrtoken.alumne_referenciat
    content = [{
        "id": alumne.id,
        "darrera_sincronitzacio": qrtoken.darrera_sincronitzacio,
    }]

    presencies_notificar = EstatControlAssistencia.objects.filter(codi_estat__in=['F', 'R', 'J'])
    faltes_assistencia = (ControlAssistencia
                          .objects
                          .filter( alumne = alumne,  estat__in = presencies_notificar, impartir__dia_impartir__month=mes )
                          .select_related('impartir',  # dia
                                          'impartir__horari__assignatura',  # materia
                                          'impartir__horari__hora',  # franja
                                          'estat',  # tipus
                                          )
                          .order_by('-impartir__dia_impartir', '-impartir__horari__hora')
                          )

    content = content + [{"dia": "/".join([str(f.impartir.dia_impartir.day), str(f.impartir.dia_impartir.month),
                                           str(f.impartir.dia_impartir.year)]),
                          "materia": str(f.impartir.horari.assignatura),
                          "hora": str(f.impartir.horari.hora),
                          "professor": str(f.professor),
                          "text": "Falta d'assistència" if str(f.estat) == "Falta" else "Retard",
                          "tipus": str(f.estat)}
                         for f in faltes_assistencia]



    incidencies = (alumne
                   .incidencia_set
                   .filter(dia_incidencia__month=mes)
                   .select_related('tipus',  # tipus
                                   'franja_incidencia',  # franja
                                   )
                   .order_by('-dia_incidencia', '-franja_incidencia')
                   )


    content = content + [{'dia': "/".join(
        [str(i.dia_incidencia.day), str(i.dia_incidencia.month), str(i.dia_incidencia.year)]),
                          'hora': str(i.franja_incidencia),
                          'professor': str(i.professional),
                          'text': i.descripcio_incidencia,
                          'tipus': str(i.tipus)}
                         for i in incidencies]


    # "Expulsions": [],
    expulsions = alumne.expulsio_set.filter(dia_expulsio__month=mes).exclude(estat='ES')
    content = content + [
        {'dia': "/".join([str(i.dia_expulsio.day), str(i.dia_expulsio.month), str(i.dia_expulsio.year)]),
         'hora': str(i.franja_expulsio),
         'professor': str(i.professor),
         'text': i.motiu,
         'tipus': "Expulsió"}
        for i in expulsions]

    # "Sancions": [],
    sancions = alumne.sancio_set.filter(impres=True, data_carta__month=mes)
    content = content + [
        {'dia': "/".join([str(i.data_carta.day), str(i.data_carta.month), str(i.data_carta.year)]),
         'hora': str(i.franja_inici),
         'professor': str(i.professor),
         'text': "Del {0} al {1}. Motiu: {2}".format(str(datetime.strftime(i.data_inici,'%d/%m/%Y')), str(datetime.strftime(i.data_fi,'%d/%m/%Y')), str(i.motiu)),
         'tipus': "Sanció"}
        for i in sancions]

    # "Activitats": [],
    sortides = NotificaSortida.objects.filter(alumne=alumne)
    #content["sortides"] = [ ] #TODO

    # "Qualitatives": [],
    avui = datetime.now().date()
    qualitatives_en_curs = [q for q in AvaluacioQualitativa.objects.all()
                            if (bool(q.data_obrir_portal_families) and
                                bool(q.data_tancar_tancar_portal_families) and
                                q.data_obrir_portal_families <= avui <= q.data_tancar_tancar_portal_families
                                )
                            ]
    respostes_qualitativa = (alumne
                             .respostaavaluacioqualitativa_set
                             .filter(qualitativa__in=qualitatives_en_curs)
                             )
    #content["Qualitatives"] = [ ] #TODO

    # Anoto canvis
    #qrtoken.darrera_sincronitzacio = ara

    #qrtoken.save()

    return Response(content)




@api_view(['POST'])
@permission_classes(( EsUsuariDeLaAPI, ))
def notificacions_news(request, format=None):
    """
    Rep la darrera data de sincronització (i un jwt), i retorna si hi ha novetats o no
    """
    data = JSONParser().parse(request)
    serializer = DarreraSincronitzacioSerializer(data=data)
    if not serializer.is_valid():
        raise serializers.ValidationError({'error': ["ups! petició amb errors"]})

    darrera_sincronitzacio = serializer.validated_data["last_sync_date"]

    qrtoken = request.user.qrportal

    # No hi ha novetats:
    content = {"resultat":"No"} if qrtoken.novetats_detectades_moment and qrtoken.novetats_detectades_moment < darrera_sincronitzacio else {"resultat":"Sí"}

    return Response(content)




@api_view(['GET'])
@permission_classes(( EsUsuariDeLaAPI, ))
def alumnes_dades(request, format=None):

    qrtoken = request.user.qrportal
    alumne = qrtoken.alumne_referenciat
    resp1, resp2 = alumne.get_responsables(compatible=True)
    content = {"grup": unicode(alumne.grup),
               "datanaixement": "/".join([unicode(alumne.data_neixement.day), unicode(alumne.data_neixement.month),unicode(alumne.data_neixement.year)]),
               "telefon": alumne.get_telefons(),
               "responsables":[{"nom":unicode(resp1.get_nom() if resp1 else ''),
                                "mail":unicode(resp1.get_correu_importat() if resp1 else ''),
                                "telefon":unicode(resp1.get_telefon() if resp1 else '')},
                               {"nom":unicode(resp2.get_nom() if resp2 else ''),
                                "mail":unicode(resp2.get_correu_importat() if resp2 else ''),
                                "telefon":unicode(resp2.get_telefon() if resp2 else '')}],
               "adreca": " , ".join(filter(None,[unicode(alumne.adreca), unicode(alumne.localitat), unicode(alumne.municipi)]))}
    return Response(content)



@api_view(['GET'])
@permission_classes((EsUsuariDeLaAPI,))
def sortides(request):
    """
    Retorna les activitats/pagaments de l'alumne
    """
    qrtoken = request.user.qrportal
    alumne = qrtoken.alumne_referenciat

    content = []

    sortides = alumne.notificasortida_set.all()
    sortides_on_no_assistira = alumne.sortides_on_ha_faltat.values_list('id', flat=True).distinct()
    sortides_justificades = alumne.sortides_falta_justificat.values_list('id', flat=True).distinct()
    # sortides a on s'ha convocat a l'alumne
    sortidesnotificat = Sortida.objects.filter(notificasortida__alumne=alumne).exclude(id__in=sortides_on_no_assistira).exclude(id__in=sortides_justificades)
    # sortides pagades a les que ja no s'ha convocat a l'alumne
    sortidespagadesperalumne = SortidaPagament.objects.filter(alumne=alumne, pagament_realitzat=True).values_list('sortida', flat=True).distinct()
    sortidespagadesnonotificades = (Sortida.objects.filter(id__in=sortidespagadesperalumne,
                                                          pagaments__pagament__alumne=alumne,
                                                          pagaments__pagament__pagament_realitzat=True)
                                    .exclude(notificasortida__alumne=alumne)
                                    .exclude(id__in=sortides_on_no_assistira)
                                    .exclude(id__in=sortides_justificades))
    # totes les sortides relacionades amb l'alumne
    activitats = sortidesnotificat.union(sortidespagadesnonotificades)
    # sortides que s'han de passar a l'app
    for sortida in activitats.order_by('-calendari_desde'):
        if sortida.tipus_de_pagament == 'ON':
            try:
                pagament = Pagament.objects.get(sortida=sortida, alumne=alumne)
                realitzat = pagament.pagament_realitzat
            except Pagament.DoesNotExist:
                pagament = None
                realitzat = False
        else:
            pagament = None
            realitzat = False
        content = content + [{"id": sortida.id,
                              "titol": str(sortida.titol),
                              "data": str(sortida.calendari_desde),
                              "pagament": bool(pagament),
                              "realitzat": realitzat,
                                  }]
    return Response(content)




@api_view(['GET'])
@permission_classes((EsUsuariDeLaAPI,))
def detallSortida(request, pk):
    """
    Rep el pk d'una activitat/pagament i retorna informació de l'activitat/pagament
    """
    qrtoken = request.user.qrportal
    alumne = qrtoken.alumne_referenciat
    try:
        int (pk)
        sortida = Sortida.objects.get(pk=pk)
    except:
        raise serializers.ValidationError({'error': ["Sortida inexistent"]})

    try:
        pagament = Pagament.objects.get(sortida=sortida, alumne=alumne)
        realitzat = pagament.pagament_realitzat
    except Pagament.DoesNotExist:
        pagament = None
        realitzat = False


    content = {"titol": str(sortida.titol),
                              "desde": sortida.calendari_desde.strftime( '%d/%m/%Y %H:%M' ),
                              "finsa": sortida.calendari_finsa.strftime( '%d/%m/%Y %H:%M' ),
                              "programa": "\n".join([sortida.programa_de_la_sortida, sortida.condicions_generals,sortida.informacio_pagament ]),
                              "preu": str(sortida.preu_per_alumne) if sortida.preu_per_alumne else u'0',
                              "dataLimitPagament": str(sortida.termini_pagament) if sortida.termini_pagament else '',
                              "realitzat": realitzat,
                              "idPagament": pagament.id if pagament else None
                        }
    return Response(content)