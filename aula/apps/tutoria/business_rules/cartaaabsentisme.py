# This Python file uses the following encoding: utf-8
from django.core.exceptions import ValidationError
from datetime import timedelta, date


from django.db.models.loading import get_model
from aula.apps.alumnes.named_instances import curs_any_fi


def cartaabsentisme_clean( instance ):
    '''
    
    calcular tipus:
        tipus1 = primera carta tots
        tipus2 = segona carta tots
        tipus3A = tercera carta ESO
        tipus3B = tercera carta post obligatoria
    
    '''
    errors = []
    instance.__is_update = instance.pk is not None
    
    if not instance.__is_update:
        
        if instance.data_carta is None:
            instance.data_carta = date.today()
            
        if instance.data_carta > date.today():
            errors.append(u'Revisa la data de la carta.' )
        
        #busco darrera carta:
        try:
            darrera_carta = instance.alumne.cartaabsentisme_set.exclude( carta_esborrada_moment__isnull = False ).order_by( '-carta_numero' )[0]
            darrera_carta_n = darrera_carta.carta_numero
        except IndexError:
            darrera_carta = None
            darrera_carta_n = 0
        carta_numero = darrera_carta_n + 1
        
        #data des d'on començar a comptar
        if bool( darrera_carta ):
            faltes_des_de_data = darrera_carta.faltes_fins_a_data + timedelta( days = 1 )
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
        
        #comprovo que hi ha més de 15 faltes:
        EstatControlAssistencia = get_model('presencia', 'EstatControlAssistencia')
        falta = EstatControlAssistencia.objects.get( codi_estat = 'F'  )
        nfaltes = (
                   instance
                   .alumne
                   .controlassistencia_set
                   .filter( impartir__dia_impartir__range = ( faltes_des_de_data, faltes_fins_a_data )   )
                   .filter( estat = falta )
                   .count()
                   )
        
        if nfaltes < 15:
            errors.append(u'Aquest alumne no ha acumulat 15 faltes des de la darrera carta' )

        
        #calculo tipus de carta    
        tipus_carta=None
        if 1 <= carta_numero <= 2:
            tipus_carta = 'tipus{0}'.format( carta_numero  )
        elif carta_numero == 3 and instance.alumne.cursa_obligatoria():  
            try:
                te_mes_de_16 = (curs_any_fi() - instance.alumne.data_neixement.year) > 16
            except:
                te_mes_de_16 = False
            if te_mes_de_16:
                tipus_carta = 'tipus3C'
            else:
                tipus_carta = 'tipus3A'
        elif carta_numero == 3 and not instance.alumne.cursa_obligatoria(): 
            tipus_carta = 'tipus3B'
        else:
            errors.append(u'Aquest alumne ja té tres cartes' )

        instance.carta_numero =carta_numero
        instance.tipus_carta = tipus_carta
        instance.faltes_des_de_data = faltes_des_de_data
        instance.faltes_fins_a_data = faltes_fins_a_data
        instance.nfaltes = nfaltes    
    
    if len( errors ) > 0:
        raise ValidationError(errors)    
    
                                         


