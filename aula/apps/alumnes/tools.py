# This Python file uses the following encoding: utf-8
from aula.apps.alumnes.models import Alumne, Grup
from django.db.models import Q
from aula.apps.incidencies.models import Incidencia, Expulsio, Sancio
from aula.apps.presencia.models import ControlAssistencia
from aula.apps.tutoria.models import Actuacio, SeguimentTutorial
from aula.apps.avaluacioQualitativa.models import AvaluacioQualitativa,\
    RespostaAvaluacioQualitativa
from aula.apps.usuaris.models import Accio, LoginUsuari
from datetime import date 
import datetime
from aula.apps.sortides.models import Sortida
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


def fusiona_alumnes_by_pk( pk , credentials = None):
    a = Alumne.objects.get( pk = pk )

    q_mateix_cognom = Q(                             
                    cognoms = a.cognoms  )
    q_mateix_nom = Q( 
                    nom = a.nom,
                      )            
    q_mateix_neixement = Q(
                    data_neixement = a.data_neixement
                        )
    q_mateixa_altres = Q(
                    adreca = a.adreca,
                    telefons = a.telefons,
                    localitat = a.localitat,
                    centre_de_procedencia = a.centre_de_procedencia,
                    adreca__gte= u""                             
                        )
    
    condicio1 = q_mateix_nom & q_mateix_cognom & q_mateix_neixement
    condicio2 = q_mateix_nom & q_mateix_cognom & q_mateixa_altres
    condicio3 = q_mateix_nom & q_mateixa_altres & q_mateix_neixement
    
    
    alumne_grup = Alumne.objects.filter(  
                                    condicio1 | condicio2 | condicio3
                                           ).exclude( pk = pk ).order_by( 'data_alta' )
    
    fusiona_alumnes( a, list( alumne_grup ), credentials )



    
def fusiona_alumnes( a_desti, a_fusionar , credentials = None ):
    '''
       el destí ha de ser el més vell (és baixa) perquè rebrà les dades dels nous 
    '''
    
    controls_desti = a_desti.controlassistencia_set.values_list('impartir__pk', flat=True)
    
    print a_fusionar
    
    for a in a_fusionar:

        if a.data_baixa is None:
            a_desti.data_baixa = None
            a_desti.estat_sincronitzacio = ''
            a_desti.motiu_bloqueig = ''

        #sortides
        q_convocats = Q( alumnes_convocats = a )
        q_que_no_vindran = Q( alumnes_que_no_vindran = a )
        q_justificacio = Q( alumnes_justificacio = a )
        sortides = Sortida.objects.filter( q_convocats | q_que_no_vindran | q_justificacio ).distinct()
            
        for sortida in sortides:
            sortida.credentials = credentials
            colleccions = [ sortida.alumnes_convocats, sortida.alumnes_justificacio, sortida.alumnes_que_no_vindran ]
            for colleccio in colleccions:
                if a in colleccio.all():
                    colleccio.remove(a)
                    if a_desti not in colleccio.all():
                        colleccio.add( a_desti )
            
        #dades bàsiques
        a_desti.nom = a.nom
        a_desti.cognoms = a.cognoms
        a_desti.data_neixement = a.data_neixement
        
        #portal
        if bool( a.correu_relacio_familia_pare ) :
            a_desti.correu_relacio_familia_pare = a.correu_relacio_familia_pare
        
        if bool( a.correu_relacio_familia_mare ):
            a_desti.correu_relacio_familia_mare = a.correu_relacio_familia_mare

        
        #incidències, expulsions i sancions
        Incidencia.objects.filter( alumne = a ).update( alumne = a_desti )
        Expulsio.objects.filter( alumne = a ).update( alumne = a_desti  )
        Sancio.objects.filter( alumne = a ).update( alumne = a_desti )

        
        #controls assistència        
        controls = ControlAssistencia.objects.filter( alumne = a ).exclude( impartir__pk__in = controls_desti ).values_list( 'pk', flat = True)
        for i in controls:
            ControlAssistencia.objects.filter( pk = i ).update( alumne = a_desti )

        controls_que_sobren = ControlAssistencia.objects.filter( alumne = a ).all()
        Incidencia.objects.filter( control_assistencia__in = controls_que_sobren ).update( control_assistencia = None )
        Expulsio.objects.filter( control_assistencia__in = controls_que_sobren ).update( control_assistencia = None  )
        controls_que_sobren.delete()


        #actuacions
        Actuacio.objects.filter( alumne = a ).update( alumne = a_desti )

        
        #qualitativa
        for x in list( RespostaAvaluacioQualitativa.objects.filter( alumne = a ).all() ):
            x.alumne = a_desti 
            x.alumne_id = a_desti.id
            x.credentials = credentials
            try:
                x.save()
            except IntegrityError:
                x.delete()

        if RespostaAvaluacioQualitativa.objects.filter( alumne = a ).exists():
            raise ValidationError( "No han canviat d'alumne les qualitatives" )
                        
        #seguiment tutorial
        if SeguimentTutorial.objects.filter( alumne = a ).exists():
            SeguimentTutorial.objects.filter( alumne = a_desti ).delete()                
            SeguimentTutorial.objects.filter( alumne = a ).update( alumne = a_desti )


        #portal famílies
        usuari_associat =  a.get_user_associat()
        if usuari_associat:
            if  a_desti.get_user_associat():
                Accio.objects.filter( usuari = usuari_associat ).update( usuari = a_desti.get_user_associat() )
                LoginUsuari.objects.filter( usuari = usuari_associat ).update( usuari = a_desti.get_user_associat() )
            else:
                Accio.objects.filter( usuari = usuari_associat ).delete()
                LoginUsuari.objects.filter( usuari = usuari_associat ).delete()

            a.user_associat = None
            a.save()
            User.objects.filter( id=usuari_associat.id ).delete()
                        
        #i un cop despullat de totes les seves relacions matem el nou:                        
        Alumne.objects.filter( pk = a.pk  ).delete()
    
    #desem les noves dades    
    a_desti.save()
        
        
def crea_alumne(nom, cognoms, dataNaixement, grup):
    # Exemple d'ús:
    #    from aula.apps.alumnes.tools import crea_alumne
    #    crea_alumne("Cynthia", "Martínez Camps", "4-10-1996", "2CTX")


    #Cal fer comprovacions dels paràmetres.
    a=Alumne()
    a.nom = nom
    a.cognoms = cognoms
    a.data_neixement = datetime.datetime.strptime(dataNaixement, "%d-%m-%Y").date()
    descripcioGrup = str(grup)
    grup = Grup.objects.get(descripcio_grup=descripcioGrup)
    a.grup = grup
    a.estat_sincronitzacio = 'MAN'
    a.data_alta = date.today()
    a.motiu_bloqueig = u'No sol·licitat'
    a.tutors_volen_rebre_correu = False
    a.save()

