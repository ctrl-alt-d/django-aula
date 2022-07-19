# This Python file uses the following encoding: utf-8

#threading
from threading import Thread

#Q
from django.db.models import Q

#models
from aula.apps.missatgeria.missatges_a_usuaris import FI_PROCES_AFEGIR_ALUMNES, tipusMissatge, \
    FI_PROCES_AFEGIR_ALUMNES_AMB_ERRORS, FI_PROCES_TREURE_ALUMNES, FI_PROCES_TREURE_ALUMNES_AMB_ERRORS
from aula.apps.presencia.models import Impartir, ControlAssistencia,\
    EstatControlAssistencia
from aula.apps.missatgeria.models import Missatge
from aula.apps.usuaris.models import User2Professor
from django.contrib.auth.models import Group
import traceback
from aula.utils.tools import unicode

class afegeixThread(Thread):
    
    def __init__ (self,usuari, expandir=None, alumnes=None, impartir=None, matmulla = False):
        Thread.__init__(self)
        self.expandir = expandir 
        self.alumnes = alumnes
        self.impartir = impartir
        self.flagPrimerDiaFet = False
        self.usuari = usuari
        self.matmulla = matmulla
      
    def run(self):        
        errors = []
        try:
            horaris_a_modificar = None

            if self.expandir:                
                horaris_a_modificar =  Q( horari__assignatura = self.impartir.horari.assignatura )
                horaris_a_modificar &= Q( horari__grup = self.impartir.horari.grup )
                horaris_a_modificar &= Q( horari__professor = self.impartir.horari.professor )
            else: 
                horaris_a_modificar = Q( horari = self.impartir.horari)
        
            #from presencia.models import EstatControlAssistencia
            #estat_pendent, _  = EstatControlAssistencia.objects.get_or_create( codi_estat = u'-', defaults={ u'nom_estat' : u'-----' } )
        
            #afegeixo l'alumne sempre que no hi sigui:
            a_partir_avui = Q( dia_impartir__gte = self.impartir.dia_impartir)
            
            pks = ( Impartir
                    .objects
                    .filter( horaris_a_modificar & a_partir_avui )
                    .values_list('id', flat=True)
                    .order_by( 'dia_impartir' )
                   )
            for pk in pks:
                i = Impartir.objects.get( pk = pk )
                alumnes_del_control = [ ca.alumne for ca in i.controlassistencia_set.all()]
                alumne_afegit = False
                for alumne in self.alumnes:
                    
                    if alumne not in alumnes_del_control:
    
                        if self.matmulla:
                            #esborro l'alumne de les altres imparticions de la mateixa hora:
                            mateix_alumne = Q( alumne = alumne )
                            mateixa_hora = Q( impartir__horari__hora = i.horari.hora )
                            mateix_dia = Q( impartir__dia_impartir = i.dia_impartir )
                            mateixa_imparticio = Q( impartir = i )
                            ControlAssistencia.objects.filter( mateix_alumne & mateixa_hora & mateix_dia & ~mateixa_imparticio  ).delete()
                        
                        #afegir
                        if alumne.data_baixa is None or alumne.data_baixa > i.dia_impartir:                                      
                            ca = ControlAssistencia( alumne = alumne, impartir = i)
                            #si ja han passar llista poso que falta:
                            falta = EstatControlAssistencia.objects.get( codi_estat = 'F' )
                            if i.dia_passa_llista is not None:
                                ca.estat = falta
                                ca.professor = User2Professor( self.usuari )
                            
                            ca.save()
                            alumne_afegit = True
                if i.pot_no_tenir_alumnes:
                    i.pot_no_tenir_alumnes = False
                    i.save()
                self.flagPrimerDiaFet = ( i.dia_impartir >= self.impartir.dia_impartir )


        except Exception as e:
            errors.append( traceback.format_exc() )

        finally:
            self.flagPrimerDiaFet = True
        missatge = FI_PROCES_AFEGIR_ALUMNES
        tipus_de_missatge = tipusMissatge(missatge)
        msg = Missatge( remitent = self.usuari, text_missatge = missatge.format( self.impartir.horari.assignatura ), tipus_de_missatge = tipus_de_missatge )
        importancia = 'PI'

        if len(errors)>0:
            missatge = FI_PROCES_AFEGIR_ALUMNES_AMB_ERRORS
            msg.afegeix_error([missatge.format( self.impartir ),])
            msg.tipus_de_missatge = tipusMissatge(missatge)
            importancia = 'VI'
            msg.save()
            administradors, _ = Group.objects.get_or_create( name = 'administradors' )

            msgAdmins = Missatge( remitent = self.usuari, text_missatge = missatge.format( self.impartir ) )
            msgAdmins.afegeix_error(errors)
            msgAdmins.save()
            msgAdmins.envia_a_grup(administradors, importancia)
                            
            msg.envia_a_usuari(self.usuari, importancia)
        return errors

    def primerDiaFet(self):
        return self.flagPrimerDiaFet

#---------------------------------------------------------------------------------------------------------------------------------


class treuThread(Thread):
    
    def __init__ (self,expandir=None, alumnes=None, impartir=None, matmulla = False, usuari = None):
        Thread.__init__(self)
        self.expandir = expandir
        self.alumnes = alumnes
        self.impartir = impartir
        self.flagPrimerDiaFet = False
        self.matmulla = matmulla
        self.usuari = usuari
      
    def run(self):        
        errors = []
        try:
            horaris_a_modificar = Q( horari = self.impartir.horari)
            if self.expandir:
                horaris_a_modificar  = Q( horari__assignatura = self.impartir.horari.assignatura )
                horaris_a_modificar &= Q( horari__grup = self.impartir.horari.grup )                
                horaris_a_modificar &= Q( horari__professor = self.impartir.horari.professor ) 
        
            #trec els alumnes:
            a_partir_avui = Q( dia_impartir__gte = self.impartir.dia_impartir)
            
            pks = ( Impartir
                    .objects
                    .filter( horaris_a_modificar & a_partir_avui )
                    .values_list('id', flat=True)
                    .order_by( 'dia_impartir' )
                   )
            for pk in pks:
                i = Impartir.objects.get( pk = pk )
                alumnes_a_esborrar = Q( alumne__in = self.alumnes )
                te_incidencies = Q( incidencia__isnull = False )
                te_expulsions  = Q( expulsio__isnull = False  )
                no_ha_passat_llista = Q( estat__isnull = True )
                if self.matmulla:
                    no_ha_passat_llista |=  Q( estat__codi_estat = 'F' )                    
                condicio = alumnes_a_esborrar & ~te_incidencies & ~te_expulsions & no_ha_passat_llista
                i.controlassistencia_set.filter( condicio ).delete()
                        
                self.flagPrimerDiaFet = ( i.dia_impartir >= self.impartir.dia_impartir )
                
        except Exception as e:
                errors.append(unicode(e))
        
        finally:
            self.flagPrimerDiaFet = True

        missatge = FI_PROCES_TREURE_ALUMNES
        tipus_de_missatge = tipusMissatge(missatge)
        msg = Missatge( remitent = self.usuari, text_missatge = missatge.format( self.impartir.horari.assignatura ), tipus_de_missatge = tipus_de_missatge)
        importancia = 'PI'

        if len(errors)>0:
            msg.afegeix_error(errors)
            importancia = 'VI'
            msg.save()
            administradors, _ = Group.objects.get_or_create( name = 'administradors' )
            missatge = FI_PROCES_TREURE_ALUMNES_AMB_ERRORS
            tipus_de_missatge = tipusMissatge(missatge)
            msgAdmins = Missatge( remitent = self.usuari, text_missatge = missatge.format( self.impartir ), tipus_de_missatge = tipus_de_missatge )
            msgAdmins.afegeix_error(errors)
            msgAdmins.save()
            msgAdmins.envia_a_grup(administradors, importancia)
                            
            msg.envia_a_usuari(self.usuari, importancia)

            
        return errors

    def primerDiaFet(self):
        return self.flagPrimerDiaFet



#--------------------------------------------------------



class marcaSenseAlumnesThread(Thread):
    
    def __init__ (self, expandir=None,  impartir=None,):
        Thread.__init__(self)
        self.expandir = expandir
        self.impartir = impartir
        self.flagPrimerDiaFet = False

    def run(self):        
        errors = []
        try:
            horaris_a_modificar = Q( horari = self.impartir.horari)
            if self.expandir:
                horaris_a_modificar  = Q( horari__assignatura = self.impartir.horari.assignatura )
                horaris_a_modificar &= Q( horari__grup = self.impartir.horari.grup )                
                horaris_a_modificar &= Q( horari__professor = self.impartir.horari.professor ) 
        
            #trec els alumnes:
            a_partir_avui = Q( dia_impartir__gte = self.impartir.dia_impartir)
            
            pks = ( Impartir
                    .objects
                    .filter( horaris_a_modificar & a_partir_avui )
                    .values_list('id', flat=True)
                    .order_by( 'dia_impartir' )
                   )
            for pk in pks:
                i = Impartir.objects.get( pk = pk )
                
                if not i.controlassistencia_set.exists():
                    i.pot_no_tenir_alumnes = True
                    i.save()
                        
                self.flagPrimerDiaFet = ( i.dia_impartir >= self.impartir.dia_impartir )
                
        except Exception as e:
                errors.append(unicode(e))
        
        finally:
            self.flagPrimerDiaFet = True
                
            
        return errors

    def primerDiaFet(self):
        return self.flagPrimerDiaFet








