# This Python file uses the following encoding: utf-8

from django.shortcuts import render
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from aula.appMobil.serializers import DarreraSincronitzacioSerializer

from aula.apps.alumnes.models import Alumne

from django.utils.datetime_safe import datetime

#Afegir nom d'alumne al token retornat per simplejwt
from aula.apps.presencia.models import EstatControlAssistencia, ControlAssistencia
from aula.apps.sortides.models import NotificaSortida
from aula.apps.usuaris.models import ModificationPortal
from aula.utils.tools import unicode


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)

        # Add extra responses here
        nom = Alumne.objects.get(user_associat__username=self.user.username)
        data['nom'] = str(nom)
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



@api_view(['GET'])
def notificacions_mes(request, mes, format=None):
    """
    Rep la darrera data de sincronització (i un jwt) i retorna tots valors actuals.
    """
    ara = datetime.now()
    #data = JSONParser().parse(request)


    #serializer = DarreraSincronitzacioSerializer(data=data)
    # if not serializer.is_valid():
    #     raise serializers.ValidationError("ups! petició amb errors")

    #darrera_sincronitzacio = serializer.validated_data["last_sync_date"]
    alumne= Alumne.objects.get(user_associat__username=request.user)
    myportaltoken, created = ModificationPortal.objects.get_or_create(alumne_referenciat=alumne)


    # No hi ha novetats:
    # print (myportaltoken.novetats_detectades_moment, " , ", darrera_sincronitzacio)
    # if myportaltoken.novetats_detectades_moment and myportaltoken.novetats_detectades_moment <= darrera_sincronitzacio:
    #     content = {"status": "All is up-to-date"}
    #     return Response(content, content_type='application/json; charset=UTF-8')

    # Sí hi ha novetats, s'envia tot:
    alumne = myportaltoken.alumne_referenciat
    content = [{
        "id": alumne.id,
        "darrera_sincronitzacio": myportaltoken.darrera_sincronitzacio,
    }]

    presencies_notificar = EstatControlAssistencia.objects.filter(codi_estat__in=['F', 'R'])
    faltes_assistencia = (ControlAssistencia
                          .objects
                          .filter(alumne=alumne, estat__in=presencies_notificar, impartir__dia_impartir__month=mes)
                          .select_related('impartir',  # dia
                                          'impartir__horari__assignatura',  # materia
                                          'impartir__horari__hora',  # franja
                                          'estat',  # tipus
                                          )
                          .order_by('-impartir__dia_impartir', '-impartir__horari__hora')
                          )
    content = content + [{'dia': "/". join([unicode(f.impartir.dia_impartir.day), unicode(f.impartir.dia_impartir.month), unicode(f.impartir.dia_impartir.year)]),
                               'materia': unicode(f.impartir.horari.assignatura),
                               'hora': unicode(f.impartir.horari.hora),
                               'professor': unicode(f.professor),
                               'text': "Falta d'assistència" if unicode(f.estat) == "Falta" else "Retard",
                               'tipus': unicode(f.estat)}
                              for f in faltes_assistencia]

    incidencies = (alumne
                   .incidencia_set
                   .filter(dia_incidencia__month=mes)
                   .select_related('tipus',  # tipus
                                   'franja_incidencia',  # franja
                                   )
                   .order_by('-dia_incidencia', '-franja_incidencia')
                   )

    content = content + [{'dia': "/".join([unicode(i.dia_incidencia.day), unicode(i.dia_incidencia.month),unicode(i.dia_incidencia.year)]),
                            'hora': unicode(i.franja_incidencia),
                            'professor' : unicode(i.professional),
                            'text': i.descripcio_incidencia,
                            'tipus': unicode(i.tipus)}
                        for i in incidencies]

    # "Expulsions": [],
    expulsions = alumne.expulsio_set.filter(dia_expulsio__month=mes).exclude(estat='ES')
    content = content + [{'dia': "/".join([unicode(i.dia_expulsio.day), unicode(i.dia_expulsio.month),unicode(i.dia_expulsio.year)]),
                            'hora': unicode(i.franja_expulsio),
                            'professor' : unicode(i.professor),
                            'text': i.motiu,
                            'tipus': "expulsió"}
                        for i in expulsions]

    # "Sancions": [],
    # sancions = alumne.sancio_set.filter(impres=True)
    # content= content + []  # TODO

    # "Activitats": [],
    # sortides = NotificaSortida.objects.filter(alumne=alumne)
    # content = content + []  # TODO

    # "Qualitatives": [],
    # avui = datetime.now().date()
    # qualitatives_en_curs = [q for q in AvaluacioQualitativa.objects.all()
    #                         if (bool(q.data_obrir_portal_families) and
    #                             bool(q.data_tancar_tancar_portal_families) and
    #                             q.data_obrir_portal_families <= avui <= q.data_tancar_tancar_portal_families
    #                             )
    #                         ]
    # respostes_qualitativa = (alumne
    #                          .respostaavaluacioqualitativa_set
    #                          .filter(qualitativa__in=qualitatives_en_curs)
    #                          )
    # content["Qualitatives"] = []  # TODO

    # Anotem canvis
    myportaltoken.darrera_sincronitzacio = ara
    myportaltoken.save()

    return Response(content, content_type='application/json; charset=UTF-8')





@api_view(['POST'])
# @permission_classes((EsUsuariDeLaAPI,))
def notificacions_news(request, format=None):
    """
    Rep la darrera data de sincronització (i un jwt) i retorna tots valors actuals.
    """
    data = JSONParser().parse(request)


    serializer = DarreraSincronitzacioSerializer(data=data)
    if not serializer.is_valid():
        raise serializers.ValidationError("ups! petició amb errors")

    darrera_sincronitzacio = serializer.validated_data["last_sync_date"]
    alumne= Alumne.objects.get(user_associat__username=request.user)
    myportaltoken, created = ModificationPortal.objects.get_or_create(alumne_referenciat=alumne)


    # Detectem novetats:

    content = {"resultat": "Sí"} if (myportaltoken.novetats_detectades_moment and myportaltoken.novetats_detectades_moment > darrera_sincronitzacio) else {"resultat": "No"}

    return Response(content, content_type='application/json; charset=UTF-8')






@api_view(['GET'])
def alumnes_dades(request, format=None):

    alumne= Alumne.objects.get(user_associat__username=request.user)

    content = {"grup": unicode(alumne.grup),
               "datanaixement": "/".join([unicode(alumne.data_neixement.day), unicode(alumne.data_neixement.month),unicode(alumne.data_neixement.year)]),
               "telefon": alumne.telefons,
               "responsables":[{"nom":alumne.rp1_nom,
                                "mail":alumne.rp1_correu,
                                "tfn": " , ".join(filter(None,[alumne.rp1_telefon,alumne.rp1_mobil]))},
                               {"nom":alumne.rp2_nom,
                                "mail":alumne.rp2_correu,
                                "tfn": " , ".join(filter(None,[alumne.rp2_telefon,alumne.rp2_mobil]))}],
               "adreça": " , ".join(filter(None,[alumne.adreca, alumne.localitat, alumne.municipi]))}

    return Response(content)