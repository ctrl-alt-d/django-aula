from aula.apps.alumnes.named_instances import curs_any_fi
from datetime import timedelta, datetime
from django.apps import apps
from django.conf import settings
from aula.apps.missatgeria.missatges_a_usuaris import ALUMNE_GENERAR_CARTA, tipusMissatge
from django.contrib.auth.models import User
from django.urls import reverse

def calcular_dades_carta(alumne, data_carta=None):
    if data_carta is None:
        data_carta = datetime.today().date()

    errors = []

    if data_carta and data_carta > datetime.today().date(): errors.append(u'Revisa la data de la carta.' )
    EstatControlAssistencia = apps.get_model('presencia', 'EstatControlAssistencia')
    falta = EstatControlAssistencia.objects.get(codi_estat='F')

    # Determinar darrera carta i data d'inici de faltes
    try:
        darrera_carta = alumne.cartaabsentisme_set.exclude(carta_esborrada_moment__isnull=False).order_by('-carta_numero')[0]
        carta_numero = darrera_carta.carta_numero + 1
        faltes_des_de_data = darrera_carta.faltes_fins_a_data + timedelta(days=1)
    except IndexError:
        darrera_carta = None
        carta_numero = 1
        faltes_des_de_data = alumne.grup.curs.data_inici_curs

    # Determinar data de fi i nombre de faltes
    try:
        faltes_fins_a_data = (
                                 alumne
                                 .controlassistencia_set
                                 .filter( impartir__dia_impartir__lte = data_carta )
                                 .values_list( 'impartir__dia_impartir', flat=True )
                                 .order_by( '-impartir__dia_impartir')
                                 .distinct()[3]
                                 )
    except IndexError:
        faltes_fins_a_data = data_carta - timedelta( days = 3 )


    nfaltes = (
        alumne.controlassistencia_set.filter(impartir__dia_impartir__range=(faltes_des_de_data, faltes_fins_a_data))
        .filter(estat=falta)
        .count()
    )

    # Calcular tipus de carta i llindar per generació de carta
    tipus_carta = None
    try:
        te_mes_de_16 = (curs_any_fi() - alumne.data_neixement.year) > 16
    except:
        te_mes_de_16 = False
    assolitMaxCartes= False
    perNivell = True if len(settings.CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA) > 0 else False
    if perNivell:
            faltes = settings.CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA.get(alumne.getNivellCustom())
            maxCartes = len(faltes) if faltes else 0
            index = carta_numero if data_carta is None else carta_numero - 1
            llindar = faltes[index] if carta_numero <= maxCartes else 0
            tipus_carta=''
            if carta_numero>maxCartes and maxCartes>0:
                errors.append(u'Aquest alumne ha arribat al màxim de cartes' )
                assolitMaxCartes = True
            else:
                if llindar==0:
                    errors.append(u"Error triant la carta a enviar a la família. Alumne {0}, sense nombre màxim de faltes per enviar carta".formnat(alumne))
    else:
            if False:
                pass
            elif carta_numero in [1,2,] and alumne.cursa_nivell(u"ESO"):
                tipus_carta = 'tipus{0}'.format( carta_numero  )
            elif carta_numero == 3 and alumne.cursa_nivell("ESO"):
                tipus_carta = 'tipus3A' if not te_mes_de_16 else 'tipus3C'
            elif carta_numero in [1,2,3,] and alumne.cursa_nivell(u"BTX"):
                tipus_carta = 'tipus3B'
            elif carta_numero in [1,2,3,] and alumne.cursa_nivell(u"CICLES"):
                tipus_carta = 'tipus3D'
            elif carta_numero in [1,2,3,]:
                errors.append(u"Error triant la carta a enviar a la família. Alumne {0}, sense nivell assignat".format(alumne))
            else:
                errors.append(u'Aquest alumne ha arribat al màxim de cartes' )
                assolitMaxCartes = True
            llindar = settings.CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA.get(tipus_carta,
                                                                          settings.CUSTOM_FALTES_ABSENCIA_PER_CARTA)

    return {
        'carta_numero': carta_numero,
        'tipus_carta': tipus_carta,
        'faltes_des_de_data': faltes_des_de_data,
        'faltes_fins_a_data': faltes_fins_a_data,
        'nfaltes': nfaltes,
        'llindar': llindar,
        'errors': errors,
        'assolitmaxcartes': assolitMaxCartes
    }


def enviar_missatge_tutor(alumne):
    #Envia un missatge als tutors d'un alumne sobre una carta d'absentisme.
    tutors = alumne.tutorsDeLAlumne()
    missatge = ALUMNE_GENERAR_CARTA
    txt = missatge.format(alumne)
    enllac = reverse('tutoria__cartes_assistencia__gestio_cartes')
    tipus_de_missatge = tipusMissatge(missatge)

    Missatge = apps.get_model('missatgeria', 'Missatge')
    usuari_notificacions, new = User.objects.get_or_create(username='TP')
    if new:
        usuari_notificacions.is_active = False
        usuari_notificacions.first_name = "Usuari Tasques Programades"
        usuari_notificacions.save()

    msg = Missatge(
        remitent=usuari_notificacions,
        text_missatge=txt,
        enllac=enllac,
        tipus_de_missatge=tipus_de_missatge,
    )

    for tutor in tutors:
        importancia = 'VI'  # Nivel de importancia
        msg.envia_a_usuari(tutor, importancia)
        print("Enviat missatge al tutor/a {0}, de l'alumne/a {1}".format(tutor,alumne))

def avisTutorCartaPerFaltes():
    from aula.apps.alumnes.models import Alumne
    totalcartes = 0
    for alumne in Alumne.objects.filter(data_baixa__isnull=True):
        dades_carta = calcular_dades_carta(alumne)
        if not dades_carta['assolitmaxcartes'] and dades_carta['nfaltes'] >= dades_carta['llindar']:
            enviar_missatge_tutor(alumne)
            totalcartes += 1
    print(f"Total missatges enviats: {totalcartes}")
