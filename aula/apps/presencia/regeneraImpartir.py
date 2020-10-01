# This Python file uses the following encoding: utf-8

#--
from aula.apps.alumnes.models import  Curs
from aula.apps.horaris.models import Horari, FranjaHoraria
from aula.apps.missatgeria.missatges_a_usuaris import FI_REPROGRAMACIO_CLASSES, tipusMissatge
from aula.apps.presencia.models import Impartir
from threading import Thread
from aula.utils import tools
from aula.utils.tools import unicode
from django.db.models import Q
from aula.apps.horaris.helpers import esFestiu
import traceback


#http://docs.python.org/library/sets.html
class regeneraThread(Thread):
    
    def __init__ (self,data_inici=None, franja_inici=None, user=None):
        Thread.__init__(self)
        self.data_inici = data_inici
        self.franja_inici = franja_inici
        self.user = user
        self.str_status=None
        
      
    def run(self):        
        #es tracta de renovar la taula 'impartir' classes. Es fa per grups i dies:
        
        tools.lowpriority()
        
        errors=[]
        warnings=[]
        infos=[]
 
        nHorarisInsertats = 0
        #estat_pendent, created = EstatControlAssistencia.objects.get_or_create( codi_estat = u'-', defaults={ u'nom_estat' : u'-----' } )
        try:
            
            import aula.apps.horaris.models as horaris
            
            #busco primer i darrer dia de classe i primera franja horària:
            from django.db.models import Min, Max
            dates = Curs.objects.aggregate( Min( 'data_inici_curs' ), Max( 'data_fi_curs' ) )
            dia_inici_curs = dates['data_inici_curs__min']
            data_fi_curs   = dates['data_fi_curs__max']
            if not self.franja_inici:
                self.franja_inici = FranjaHoraria.objects.order_by('hora_inici','hora_fi').first()
            import datetime as t

            #calculo rang de dates a refer               
            self.data_inici = dia_inici_curs if ( not self.data_inici or dia_inici_curs > self.data_inici ) else self.data_inici
            total_dies = ( data_fi_curs - self.data_inici ).days 
            
            #calculo tots els dies a refer
            delta = t.timedelta( days = +1)
            totsElsDies = []
            dia = self.data_inici
            while dia <= data_fi_curs:
                totsElsDies.append(dia)
                dia += delta
                
            #per tots els dies:
            for dia in totsElsDies:

                #print 'processant dia: ' + unicode( dia ) #debug 

                #estatus de l'actualització                
                dies_fets = ( dia - self.data_inici ).days
                tpc =  float( dies_fets ) / float( total_dies) if total_dies else 1.0 
                self.str_status = u'Processant dia %s (%dtpc) %d dies de %d ' % (  unicode(dia), int(tpc * 100), dies_fets , total_dies   ) 
                
                #print self.str_status
                
                #esborrar els impartir d'aquell dia (d'horaris donats de baixa)
                horari_donat_de_baixa = Q( horari__es_actiu = False )
                mateix_dia = Q( dia_impartir = dia )
                condicio_esborrat = horari_donat_de_baixa & mateix_dia
                if dia == self.data_inici:
                    franja_anterior = Q( horari__hora__hora_inici__gte=self.franja_inici.hora_inici )
                    condicio_esborrat = condicio_esborrat & franja_anterior
                Impartir.objects.filter( condicio_esborrat ).delete()
            
                #per tots els horaris d'aquell dia: crear impartir
                horari_actiu = Q( es_actiu = True )
                horari_del_dia_de_la_setmana = Q( dia_de_la_setmana__n_dia_ca = dia.weekday() )
                for horari in Horari.objects.filter( horari_actiu & horari_del_dia_de_la_setmana   ):
                    fora_de_rang = (dia == self.data_inici ) and  (horari.hora.hora_inici <  self.franja_inici.hora_inici )
                    curs = horari.grup.curs if horari.grup else None
                    dia_festa = esFestiu( curs=curs, dia=dia, hora=horari.hora )
                    if not fora_de_rang :
                        if not dia_festa:
                            impartir_modificat , created = Impartir.objects.get_or_create( dia_impartir = dia, 
                                                                          horari = horari ) 
                            if created: 
                                nHorarisInsertats += 1

                            if not created:
                                aula_horari = horari.aula.pk if horari.aula else -1
                                aula_impartir = impartir_modificat.reserva.aula.pk if impartir_modificat.reserva else -1
                                canvi_aula = ( aula_horari != aula_impartir )
                                if canvi_aula:
                                    if (impartir_modificat.reserva and
                                     not impartir_modificat.reserva.es_reserva_manual):
                                        fake_l4_credentials = (None, True)
                                        impartir_modificat.reserva.credentials = fake_l4_credentials
                                        impartir_modificat.reserva.delete()
                                        impartir_modificat.reserva = None
                                        impartir_modificat.reserva_id = None
                                    impartir_modificat.save()
                        else:
                            Impartir.objects.filter( dia_impartir = dia, horari = horari ).delete()
                    else:
                        pass
                        #print 'fora de rang:' + unicode( horari )  #debug


        except Exception as e:
            errors.append( traceback.format_exc() )
            #errors.append(unicode(e))
            self.str_status = unicode(e)
        
        self.str_status = u'Finalitzat' + unicode( errors )
        
        infos.append(u'Regeneració finalitzada')
        infos.append(u'%d horaris insertats'% nHorarisInsertats)

        #Deixar missatge a la base de dades (utilitzar self.user )
        from aula.apps.missatgeria.models import Missatge
        missatge = FI_REPROGRAMACIO_CLASSES
        tipus_de_missatge = tipusMissatge(missatge)
        msg = Missatge( 
                    remitent= self.user, 
                    text_missatge = missatge,
                    tipus_de_missatge = tipus_de_missatge)
        msg.afegeix_errors( errors )
        msg.afegeix_warnings(warnings)
        msg.afegeix_infos(infos)    
        importancia = 'VI' if len( errors )> 0 else 'IN'
        msg.envia_a_usuari(self.user, importancia=importancia)

    def status(self):
        return self.str_status

