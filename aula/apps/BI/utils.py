# This Python file uses the following encoding: utf-8
from aula.apps.alumnes.models import Alumne, Curs
from django.conf import settings
import csv
import os.path
from aula.apps.usuaris.models import Professor
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.presencia.models import ControlAssistencia
from aula.apps.assignatures.models import Assignatura
from django.utils.datetime_safe import datetime
import datetime as t
from datetime import date
import hashlib
from django.template.defaultfilters import slugify



#Dims:
# Alumnes: id, id_nivell, nivell, id_curs, curs, id_grup, grup,
# Franja Horaria: id, nom, mati_tarda_vespre
# Assignatures: id, nom
# Professors: id, username, nom, cognoms
# Data: dia, curs, any, mes, dia, trimestre
#
#Fact:
# controls: n_classes,n_assistencies, n_faltes_totals, n_faltes_no_justificades, n_retards, n_justificades
# incidencies: n_informatives, n_incidencies, n_expulsions, n_expulsions_centre
# actuacions: n_actuacions_alumne, n_actuacions_familia
# portal families: n_connexions, n_enviaments, t_resposta

def export_bi():
    '''
    
      create table alumnes (
            id int,
            nivell varchar(50),
            curs varchar(50),
            grup varchar(90),
            alumne_alias varchar(50),
            alumne_nom varchar(200),
            alumne_hash varchar(100)
        );

       create table dates (
            id int,
            data date,
            dia int,
            mes int,
            year int,
            setmana int           
        );

        create table franges (
            id int,
            hora_inici varchar(20)
        );

        create table professors (
            id int,
            professor varchar(100),
            email varchar(100)
        );       

        create table assignatures (
            id int,
            assignatura varchar(200)
        );       

        create table controls (
            id int,
            alumne_id int,
            assignatura_id int,
            professor_id int,
            data_id int,
            franja_id int,
            n_total_classes int,
            n_de_classes int,
            n_assistencies int,
            n_faltes_totals int,
            n_faltes_no_justificades int,
            n_faltes_justificades int,
            n_retards int
        ); 




      
   '''
    dim_alumnes()
    dim_assignatures()
    dim_franges()   
    dim_professors()
    fact_controls()

# Alumnes: id, id_nivell, nivell, id_curs, curs, id_grup, grup,
def dim_alumnes( ):
    file_name = os.path.join( settings.BI_DIR, 'alumnes.csv')
    ofile = open(file_name, 'wb')
    writer = csv.writer(ofile)
    for alumne in Alumne.objects.all():

        alumne_row = []
        alumne_row.append( any_inici_curs() )
        alumne_row.append( any_inici_curs() * 10000000 + alumne.pk )
        alumne_row.append( alumne.grup.curs.nivell.pk )
        alumne_row.append( alumne.grup.curs.nivell.nom_nivell )
        alumne_row.append( alumne.grup.curs.pk )
        alumne_row.append( alumne.grup.curs.nom_curs )
        alumne_row.append( alumne.grup.pk )
        alumne_row.append( alumne.grup.descripcio_grup )
        alumne_row.append( 'alumne'+str( alumne.pk ) )
        alumne_row.append( alumne.cognoms + ', '+ alumne.nom )
        writer.writerow( alumne_row ) 
            
    ofile.close()    

# Franja Horaria: id, nom, mati_tarda_vespre 
def dim_franges( ):
    file_name = os.path.join( settings.BI_DIR, 'franges.csv')
    ofile = open(file_name, 'wb')
    writer = csv.writer(ofile)
    for element in FranjaHoraria.objects.all():

        element_row = []
        element_row.append( any_inici_curs() )
        element_row.append( any_inici_curs() * 10000000 + element.pk )
        element_row.append( element.hora_inici )
        element_row.append( element.hora_fi )
        element_row.append( element.nom_franja )
        writer.writerow( element_row ) 
    
    ofile.close()    

# Professors: id, username, nom, cognoms   
def dim_professors( ):
    file_name = os.path.join( settings.BI_DIR, 'professors.csv')
    ofile = open(file_name, 'wb')
    writer = csv.writer(ofile)
    for element in Professor.objects.all():

        element_row = []
        element_row.append( any_inici_curs() )
        element_row.append( any_inici_curs() * 10000000 + element.pk  )
        element_row.append( element.username )
        element_row.append( element.first_name )
        element_row.append( element.last_name )
        writer.writerow( element_row ) 
    
    ofile.close()    
    
# Assignatures: id, nom
def dim_assignatures( ):    
    file_name = os.path.join( settings.BI_DIR, 'assignatures.csv')
    ofile = open(file_name, 'wb')
    writer = csv.writer(ofile)
    for element in Assignatura.objects.all():

        element_row = []
        element_row.append( any_inici_curs() )
        element_row.append( any_inici_curs() * 10000000 + element.pk )
        element_row.append( element.codi_assignatura )
        writer.writerow( element_row ) 
    
    ofile.close()    

# Data: dia, curs, any, mes, dia, trimestre        


#---------------------------------------------------------- DADES per a BI -----------------------------------------------------
# controls: n_classes,n_assistencies, n_faltes_totals, n_faltes_no_justificades, n_retards, n_justificades
def fact_controls( n = -1 , flag_impersona = False ): 
    debug = n
    file_name = os.path.join( settings.BI_DIR, 'controls.csv')
    ofile = open(file_name, 'wb')
    writer = csv.writer(ofile)
    
    element_row = []
    
    element_row.append( 'any_inici_curs') 
    element_row.append( 'data') 
    element_row.append( 'alumne_disociat' )
    element_row.append( 'nom' )
    element_row.append( 'nom_nivell' )
    element_row.append( 'nom_curs' )
    element_row.append( 'descripcio_grup' )
    element_row.append( 'codi_assignatura' )
    
    #franja
    element_row.append( 'hora_inici' )
    element_row.append( 'hora_fi' )
    
    #professor        
    element_row.append( 'professor'  )
    element_row.append( 'email'  )
    
    #facts ---      
    element_row.append( 'n_total_classes' )
    element_row.append( 'n_de_classes' )
    element_row.append( 'n_assistencies' )
    element_row.append( 'n_faltes_totals' )
    element_row.append( 'n_faltes_no_justificades' )
    element_row.append( 'n_faltes_justificades' )
    element_row.append( 'n_retards' )

    writer.writerow( element_row ) 

    tots_els_controls_assistencia = ( ControlAssistencia
                                      .objects
                                      .exclude( alumne__data_baixa__isnull = False )
                                      .values_list('id', flat=True)
                                      .order_by( 'impartir__dia_impartir' )
                                    )
    
    for pk in tots_els_controls_assistencia:
        element = ControlAssistencia.objects.get( pk = pk )
        debug -= 1
        if debug == 0:
            break
        element_row = []
        
        #any_inici_curs
        element_row.append( any_inici_curs() )
        
        #data
        element_row.append( element.impartir.dia_impartir )
        
        #alumne_disociat
        element_row.append( '{0}-{1}'.format( any_inici_curs() , element.alumne.pk ) )

        #alumne
        cognoms_nom = element.alumne.cognoms + u', '+ element.alumne.nom
        if flag_impersona:
            cognoms_nom = hashlib.sha224( slugify( cognoms_nom ) )
        element_row.append( slugify(cognoms_nom ) )

        #nivell
        element_row.append( element.alumne.grup.curs.nivell.nom_nivell )
        
        #curs
        element_row.append( element.alumne.grup.curs.nom_curs )
        
        #grup
        element_row.append( element.alumne.grup.descripcio_grup )
        
        #assignatura
        element_row.append( element.impartir.horari.assignatura.codi_assignatura )
        
        #franja
        element_row.append( element.impartir.horari.hora.hora_inici )
        element_row.append( element.impartir.horari.hora.hora_fi )
        
        #professor        
        element_row.append( element.impartir.professor_passa_llista.username if element.impartir.professor_passa_llista else  
                            element.impartir.horari.professor.username  )
        
        element_row.append( element.impartir.professor_passa_llista.email if element.impartir.professor_passa_llista else  
                            element.impartir.horari.professor.email )
        
        #facts ---
        nTotalDeClasses = 1        
        element_row.append( nTotalDeClasses )

        nDeClasses = 1 if element.estat is not None else 0
        element_row.append( nDeClasses )
        
        nAssistencies = 1 if element.estat is not None and element.estat.codi_estat in ( 'P','R','O') else 0
        element_row.append( nAssistencies )
        
        nFaltesTotes = 1 if element.estat is not None and element.estat.codi_estat in ( 'F','J') else 0
        element_row.append( nFaltesTotes )
        
        nFaltesNoJustificades = 1 if element.estat is not None and element.estat.codi_estat in ( 'F') else 0
        element_row.append( nFaltesNoJustificades )
        
        nFaltesJustificades = 1 if element.estat is not None and element.estat.codi_estat in ( 'J') else 0
        element_row.append( nFaltesJustificades )
        
        nRetards = 1 if element.estat is not None and element.estat.codi_estat in ( 'R') else 0
        element_row.append( nRetards )

        writer.writerow( element_row ) 
    
    ofile.close()
    


#-------------------------------------------- DADES per al Em sento afortunat ---------------------------------------
def fact_controls_dissociats( n=-1 ): 
    debug = n
    file_name = os.path.join( settings.BI_DIR, 'controls_dissociats.csv')
    ofile = open(file_name, 'wb')
    writer = csv.writer(ofile)
    
    element_row = []
    
    columnes = [    
             'nom_nivell' ,
             'hora_inici' ,
             'assistenciaMateixaHora1WeekBefore' ,
             'assistenciaMateixaHora2WeekBefore' ,
             'assistenciaMateixaHora3WeekBefore' ,
             'assistenciaaHoraAnterior' ,
             'assistencia' ]
    for c in columnes:
        element_row.append( c )
    writer.writerow( element_row ) 
 
    pks =  ( ControlAssistencia
             .objects
             .exclude( alumne__data_baixa__isnull = False )
             .filter(
                   impartir__dia_impartir__lt =  datetime.today(),
                   impartir__dia_impartir__gt =  date( year = 2012, month = 10, day = 1 )  
                       )
             .values_list('id', flat=True)
             .order_by( 'impartir__dia_impartir' )
            )
    
    for pk in pks:
        element = ControlAssistencia.objects.get( pk = pk )
        debug -= 1
        if debug == 0:
            break

        row = []
            
        dades = dades_dissociades(element) 
        for c in columnes:
            row.append( dades[c] )
        writer.writerow( row ) 
    
    ofile.close()
    
def dades_dissociades( element ):

    element_dict = {}
    
    element_dict['nom_nivell'] =  element.alumne.grup.curs.nivell.nom_nivell 
    
    element_dict['hora_inici'] =  element.impartir.horari.hora.hora_inici 
    
    #setmanes anteriors
    fa1Setmana = element.impartir.dia_impartir - t.timedelta( days = 7 )
    fa2Setmana = element.impartir.dia_impartir - t.timedelta( days = 14 )
    fa3Setmana = element.impartir.dia_impartir - t.timedelta( days = 21 )
    
    try:
        elementfa1Setmana =  ControlAssistencia.objects.filter( 
                                                            alumne = element.alumne,
                                                            impartir__horari__hora = element.impartir.horari.hora, 
                                                            impartir__dia_impartir = fa1Setmana,  
                                                            impartir__horari__assignatura = element.impartir.horari.assignatura )
    except ControlAssistencia.DoesNotExist:
        elementfa1Setmana = None
    esFaltaMateixaHora1WeekBefore = PresenciaQuerySet( elementfa1Setmana  )

    try:
        elementfa2Setmana =  ControlAssistencia.objects.filter( 
                                                            alumne = element.alumne,                                                                
                                                            impartir__horari__hora = element.impartir.horari.hora, 
                                                            impartir__dia_impartir = fa2Setmana,  
                                                            impartir__horari__assignatura = element.impartir.horari.assignatura )
    except ControlAssistencia.DoesNotExist:
        elementfa2Setmana = None
    esFaltaMateixaHora2WeekBefore = PresenciaQuerySet( elementfa2Setmana  )

    try:
        elementfa3Setmana =  ControlAssistencia.objects.filter( 
                                                            alumne = element.alumne,                                                                
                                                            impartir__horari__hora = element.impartir.horari.hora, 
                                                            impartir__dia_impartir = fa3Setmana,  
                                                            impartir__horari__assignatura = element.impartir.horari.assignatura )
    except ControlAssistencia.DoesNotExist:
        elementfa3Setmana = None
    esFaltaMateixaHora3WeekBefore = PresenciaQuerySet( elementfa3Setmana  )

    element_dict['assistenciaMateixaHora1WeekBefore'] =  esFaltaMateixaHora1WeekBefore 
    element_dict['assistenciaMateixaHora2WeekBefore'] =  esFaltaMateixaHora2WeekBefore 
    element_dict['assistenciaMateixaHora3WeekBefore'] =  esFaltaMateixaHora3WeekBefore 

    #---Una hora abans        
    unaHora40abans = add_secs_to_time(element.impartir.horari.hora.hora_inici, -100*60)

    controls_anteriors = ControlAssistencia.objects.filter(
                                                         alumne = element.alumne, 
                                                         impartir__horari__hora__hora_inici__lt = element.impartir.horari.hora.hora_inici,
                                                         impartir__horari__hora__hora_inici__gt = unaHora40abans,
                                                         impartir__dia_impartir = element.impartir.dia_impartir  )        
    

    
    esFaltaHoraAnterior = PresenciaQuerySet( controls_anteriors )
        
    element_dict['assistenciaaHoraAnterior'] =  esFaltaHoraAnterior 

    esFalta = CalculaFalta( element )
    
    element_dict['assistencia'] =  esFalta 
    
    return element_dict
    
def CalculaFalta( element ):

    if element and element.estat is not None:
        if element.estat.codi_estat in ( 'P','R','O'):
            esFalta = 'Present' 
        else:
            esFalta = 'Absent'
    else:
        esFalta = 'NA'
    
    return esFalta

def PresenciaQuerySet( qs ):
    if qs is not None and qs.filter( estat__isnull = False  ).exists():
        if qs.filter( estat__codi_estat__in = ['P','R'] ):
            esFaltaAnterior = 'Present'
        elif qs.filter( estat__codi_estat__in = ['O'] ):
            esFaltaAnterior = 'Online'
        else:
            esFaltaAnterior = 'Absent'
    else:
        esFaltaAnterior = 'NA'
    return esFaltaAnterior


#------------

def any_inici_curs():
    return Curs.objects.filter( data_inici_curs__isnull = False )[0].data_inici_curs.year

    
def add_secs_to_time(timeval, secs_to_add):
    import datetime
    dummy_date = datetime.date(1, 1, 1)
    full_datetime = datetime.datetime.combine(dummy_date, timeval)
    added_datetime = full_datetime + datetime.timedelta(seconds=secs_to_add)
    return added_datetime.time()    
          
    