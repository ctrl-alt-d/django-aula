from aula.apps.alumnes.models import Alumne
from aula.apps.alumnes.named_instances import curs_any_fi
from datetime import timedelta, datetime
from django.apps import apps
from django.conf import settings
from aula.apps.missatgeria.missatges_a_usuaris import ALUMNE_GENERAR_CARTA, tipusMissatge
from aula.apps.missatgeria.models import Missatge
from django.contrib.auth.models import User, Group
from django.urls import reverse


def avisTutorCartaPerFaltes():
    totalcartes = 0
    for alumne in Alumne.objects.filter(data_baixa__isnull=True):
        tutors = alumne.tutorsDeLAlumne()
        cartesDeLAlumne = alumne.cartaabsentisme_set.exclude(carta_esborrada_moment__isnull=False)
        if cartesDeLAlumne:
            darrera_carta = cartesDeLAlumne.order_by('-carta_numero')[0]
            faltes_des_de_data = darrera_carta.faltes_fins_a_data + timedelta(days=1)
        else:
            faltes_des_de_data = alumne.grup.curs.data_inici_curs
            darrera_carta = None
        faltes_fins_a_data = datetime.today().date() - timedelta(days=3)

        # comprovo que hi ha més de 15 faltes:
        EstatControlAssistencia = apps.get_model('presencia', 'EstatControlAssistencia')
        falta = EstatControlAssistencia.objects.get(codi_estat='F')
        nfaltes = (
            alumne.controlassistencia_set.filter(impartir__dia_impartir__range=(faltes_des_de_data, faltes_fins_a_data))
            .filter(estat=falta)
            .count()
        )

        if darrera_carta:
            carta_numero = darrera_carta.carta_numero +1
        else:
            carta_numero = 1

        # Decideix el màxim de cartes i les faltes per carta segons el nivell i el número de la carta.
        # Fa falta CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA
        if len(settings.CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA) > 0:
            faltes = settings.CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA.get(alumne.getNivellCustom())
            if faltes is not None:
                maxCartes = len(faltes)
            else:
                maxCartes = 0
            if carta_numero <= maxCartes:
                llindar = faltes[carta_numero]
            else:
                llindar = 0
            perNivell = True
        else:
            perNivell = False  # si False, no fa servir CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA


        #càlcul del tipus de carta
        tipus_carta=None
        try:
            te_mes_de_16 = (curs_any_fi() - alumne.data_neixement.year) > 16
        except:
            te_mes_de_16 = False

        if perNivell:
            tipus_carta = ''
        else:
            if False:
                pass
            elif carta_numero in [1, 2, ] and alumne.cursa_nivell(u"ESO"):
                tipus_carta = 'tipus{0}'.format(carta_numero)
            elif carta_numero == 3 and alumne.cursa_nivell(u"ESO") and not te_mes_de_16:
                tipus_carta = 'tipus3A'
            elif carta_numero == 3 and alumne.cursa_nivell(u"ESO") and te_mes_de_16:
                tipus_carta = 'tipus3C'
            elif carta_numero in [1, 2, 3, ] and alumne.cursa_nivell(u"BTX"):
                tipus_carta = 'tipus3B'
            elif carta_numero in [1, 2, 3, ] and alumne.cursa_nivell(u"CICLES"):
                tipus_carta = 'tipus3D'
            else:
                tipus_carta = ''

            llindar = settings.CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA.get(tipus_carta,
                                                                          settings.CUSTOM_FALTES_ABSENCIA_PER_CARTA)

        if nfaltes >= llindar:
            missatge = ALUMNE_GENERAR_CARTA
            txt = missatge.format(alumne)
            enllac = reverse('tutoria__cartes_assistencia__gestio_cartes')
            tipus_de_missatge = tipusMissatge(missatge)
            Missatge = apps.get_model('missatgeria', 'Missatge')
            usuari_notificacions, new = User.objects.get_or_create(username='TP')
            if new:
                usuari_notificacions.is_active = False
                usuari_notificacions.first_name = u"Usuari Tasques Programades"
                usuari_notificacions.save()

            msg = Missatge(remitent=usuari_notificacions, text_missatge=txt, enllac=enllac,
                           tipus_de_missatge=tipus_de_missatge)
            for tutor in tutors:
                importancia = 'VI'
                msg.envia_a_usuari(tutor, importancia)
                print("Enviat missatge a tutor/a {0}, de l'alumne {1}".format(tutor, alumne))
            totalcartes += 1

    print("Total missatges enviats: {0}".format(totalcartes))

