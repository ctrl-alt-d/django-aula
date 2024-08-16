# This Python file uses the following encoding: utf-8
from django.core.exceptions import ValidationError
from datetime import timedelta, date, datetime
from django.apps import apps



from aula.apps.alumnes.named_instances import curs_any_fi
from django.conf import settings

def cartaabsentisme_clean( instance ):
    '''
    
    calcular tipus:
        tipus1 = primera carta tots
        tipus2 = segona carta tots
        tipus3A = tercera carta ESO menors 16 anys
        tipus3B = carta Batxillerat
        tipus3C = cursa obligatoria i té més de 16 anys
        tipus3D = carta Cicles

    '''
    errors = []
    instance.__is_update = instance.data_carta is not None
    llindar=0
    if not instance.__is_update:
        if instance.carta_numero>1:
            darrera_carta = instance.alumne.cartaabsentisme_set.exclude(carta_esborrada_moment__isnull=False).order_by('-carta_numero')[1]
            faltes_des_de_data = darrera_carta.faltes_fins_a_data + timedelta(days=1)
        else:
         try:
                faltes_des_de_data =(instance
                                     .alumne
                                     .controlassistencia_set
                                     .values_list( 'impartir__dia_impartir', flat=True )
                                     .order_by( 'impartir__dia_impartir')[0]
                                     )
         except IndexError:
                faltes_des_de_data =(instance
                                     .alumne
                                     .grup
                                     .curs
                                     .data_inici_curs
                                     )

        #data fins on comptar:
        if instance.data_carta:
            try:
                faltes_fins_a_data = (
                                     instance
                                     .alumne
                                     .controlassistencia_set
                                     .filter( impartir__dia_impartir__lte = instance.data_carta )
                                     .values_list( 'impartir__dia_impartir', flat=True )
                                     .order_by( '-impartir__dia_impartir')
                                     .distinct()[4]
                                     )
            except IndexError:
                faltes_fins_a_data = instance.data_carta - timedelta( days = 3 )
        else: faltes_fins_a_data = datetime.today().date() - timedelta( days = 3 )
        
        #comprovo que hi ha més de 15 faltes:
        EstatControlAssistencia = apps.get_model('presencia', 'EstatControlAssistencia')
        falta = EstatControlAssistencia.objects.get( codi_estat = 'F'  )
        nfaltes = (
                   instance
                   .alumne
                   .controlassistencia_set
                   .filter( impartir__dia_impartir__range = ( faltes_des_de_data, faltes_fins_a_data )   )
                   .filter( estat = falta )
                   .count()
                   )
        # amorilla@xtec.cat
        # Decideix el màxim de cartes i les faltes per carta segons el nivell i el número de la carta.
        # Fa falta CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA
        # No fa falta definir el tipus de carta en aquest moment, es farà al document odt
        if len(settings.CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA)>0:
            faltes = settings.CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA.get(instance.alumne.getNivellCustom())
            if faltes is not None:
                maxCartes = len(faltes)
            else:
                maxCartes = 0
            if instance.carta_numero<=maxCartes:
                llindar = faltes[instance.carta_numero-1]
            else:
                llindar=0
            perNivell=True
        else:
            perNivell=False  # si False, no fa servir CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA 

        #calculo tipus de carta    
        tipus_carta=None
        try:
            te_mes_de_16 = (curs_any_fi() - instance.alumne.data_neixement.year) > 16
        except:
            te_mes_de_16 = False

        # amorilla@xtec.cat
        if perNivell:
            tipus_carta=''
            if instance.carta_numero>maxCartes and instance.data_carta and  maxCartes>0:
                errors.append(u'Aquest alumne ha arribat al màxim de cartes' )
            else:
                if instance.data_carta and  llindar==0:
                    raise Exception(u"Error triant la carta a enviar a la família")
        else:
            
            if False:
                pass

            elif instance.carta_numero in [1,2,] and instance.alumne.cursa_nivell(u"ESO"):
                tipus_carta = 'tipus{0}'.format( instance.carta_numero  )

            elif instance.carta_numero == 3 and instance.alumne.cursa_nivell(u"ESO") and not te_mes_de_16:
                tipus_carta = 'tipus3A'

            elif instance.carta_numero == 3 and instance.alumne.cursa_nivell(u"ESO") and te_mes_de_16:
                tipus_carta = 'tipus3C'

            elif instance.carta_numero in [1,2,3,] and instance.alumne.cursa_nivell(u"BTX"):
                tipus_carta = 'tipus3B'

            elif instance.carta_numero in [1,2,3,] and instance.alumne.cursa_nivell(u"CICLES"):
                tipus_carta = 'tipus3D'

            elif instance.carta_numero in [1,2,3,] and instance.data_carta:
                raise Exception(u"Error triant la carta a enviar a la família")

            else:
                errors.append(u'Aquest alumne ha arribat al màxim de cartes' )
                tipus_carta = ''

            llindar = settings.CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA.get(instance.tipus_carta,settings.CUSTOM_FALTES_ABSENCIA_PER_CARTA)

        instance.tipus_carta = tipus_carta
        instance.faltes_des_de_data = faltes_des_de_data
        instance.faltes_fins_a_data = faltes_fins_a_data
        instance.nfaltes = nfaltes

    if instance.nfaltes < llindar:
        errors.append(u'Aquest alumne no ha acumulat {} faltes des de la darrera carta'.format(llindar))

    if len( errors ) > 0:
        raise ValidationError(errors)    
    
                                         


