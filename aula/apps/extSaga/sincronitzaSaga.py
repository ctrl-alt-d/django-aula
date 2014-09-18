# This Python file uses the following encoding: utf-8

#--
from aula.apps.alumnes.models import Alumne, Grup, Nivell
from aula.apps.presencia.models import ControlAssistencia
from aula.apps.missatgeria.models import Missatge
from aula.apps.usuaris.models import Professor

from django.db.models import Q 

from datetime import date 
from django.contrib.auth.models import Group

import csv, time
from aula.apps.extSaga.models import Grup2Aula

from django.conf import settings

def sincronitza(f, user = None):
    
    msgs = comprovar_grups( f )
    
    if msgs["errors"]:
        return msgs
    
    errors = []
        
    Alumne.objects.exclude( estat_sincronitzacio__exact = 'DEL' ).update( estat_sincronitzacio = 'PRC')
        #,"00_NOM","01_ADRE�A","02_CP","03_CENTRE PROCED�NCIA","04_CODI LOCALITAT","05_CORREU ELECTR�NIC","06_DATA NAIXEMENT","07_DOC. IDENTITAT","08_GRUPSCLASSE","09_NOM LOCALITAT","10_TEL�FONS","11_TUTOR(S)"
    reader = csv.DictReader(f)
    errors_nAlumnesSenseGrup=0
    info_nAlumnesLlegits=0
    info_nAlumnesInsertats=0
    info_nAlumnesEsborrats=0
    info_nAlumnesCanviasDeGrup=0    
    info_nAlumnesModificats=0
    info_nMissatgesEnviats = 0
    
    AlumnesCanviatsDeGrup = []
    AlumnesInsertats = []

 #,"00_NOM","01_DATA NAIXEMENT",
 #"02_ADREÇA","03_CENTRE PROCEDÈNCIA","04_GRUPSCLASSE","05_CORREU ELECTRÒNIC","06_LOCALITAT",
 #"07_TELÈFON RESP. 1","08_TELÈFON RESP. 2","09_RESPONSABLE 2","10_RESPONSABLE 1"
    
    trobatGrupClasse = False
    trobatNom = False
    trobatDataNeixement = False
    
    f.seek(0)
    for row in reader:
        info_nAlumnesLlegits+=1
        a=Alumne()
        a.telefons = ''
        a.tutors = ''
        a.correu_tutors = ''
        for columnName, value in row.iteritems():
            columnName = unicode(columnName,'iso-8859-1')
            #columnName = unicode( rawColumnName, 'iso-8859-1'  )
            uvalue =  unicode(value,'iso-8859-1')
            if columnName.endswith( u"_NOM"): 
                a.nom =uvalue.split(',')[1].lstrip().rstrip()                #nomes fins a la coma
                a.cognoms = uvalue.split(',')[0]
                trobatNom = True
            if columnName.endswith( u"_GRUPSCLASSE"):
                try:
                    unGrup = Grup2Aula.objects.get(grup_saga = uvalue, Grup2Aula__isnull = False)
                    a.grup = unGrup.Grup2Aula
                except:
                    return { 'errors': [ u"error carregant {0}".format( uvalue ), ], 'warnings': [], 'infos': [] }
                trobatGrupClasse = True
            if columnName.endswith( u"_CORREU ELECTRÒNIC")  or columnName.find( u"_ADREÇA ELECTR. RESP.")>=0 : 
                a.correu_tutors += unicode(value,'iso-8859-1') + u', '
            if columnName.endswith( u"_DATA NAIXEMENT"): 
                dia=time.strptime( unicode(value,'iso-8859-1'),'%d/%m/%Y')
                a.data_neixement = time.strftime('%Y-%m-%d', dia)
                trobatDataNeixement = True
            if columnName.endswith( u"_CENTRE PROCEDÈNCIA"): 
                a.centre_de_procedencia = unicode(value,'iso-8859-1')
            if columnName.endswith( u"_LOCALITAT"): 
                a.localitat = unicode(value,'iso-8859-1')
            if columnName.find( u"_TELÈFON RESP")>=0 or columnName.find( u"_MÒBIL RESP")>=0 or columnName.find( u"_ALTRES TELÈFONS")>=0 : 
                a.telefons += unicode(value,'iso-8859-1') + u', '
            if columnName.find( u"_RESPONSABLE")>=0: 
                a.tutors = unicode(value,'iso-8859-1') + u', '
            if columnName.endswith( u"_ADREÇA" ): 
                a.adreca = unicode(value,'iso-8859-1')
                
                
        if not (trobatGrupClasse and trobatNom and trobatDataNeixement):
            return { 'errors': [ u'Falten camps al fitxer' ], 'warnings': [], 'infos': [] }

        
        alumneDadesAnteriors = None
        try:
            q_mateix_cognom = Q(                             
                            cognoms = a.cognoms )
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
            
            
            alumneDadesAnteriors = Alumne.objects.get(  
                                            condicio1 | condicio2 | condicio3
                                               )
        except Alumne.DoesNotExist:
            pass
        
        if alumneDadesAnteriors is None:
            a.estat_sincronitzacio = 'S-I'
            a.data_alta = date.today()
            a.motiu_bloqueig = u'No sol·licitat'
            a.tutors_volen_rebre_correu = False            

            info_nAlumnesInsertats+=1
            AlumnesInsertats.append(a)
            
        else:
            #TODO: si canvien dades importants avisar al tutor. 
            a.pk = alumneDadesAnteriors.pk
            a.estat_sincronitzacio = 'S-U'
            info_nAlumnesModificats+=1
            if settings.CUSTOM_MODIFICAR_GRUP_IMPORTACIO_SAGA and a.grup.pk  != alumneDadesAnteriors.grup.pk:
                AlumnesCanviatsDeGrup.append(a)
            a.user_associat = alumneDadesAnteriors.user_associat
            #el recuperem, havia estat baixa:
            if alumneDadesAnteriors.data_baixa:
                info_nAlumnesInsertats+=1
                a.data_alta = date.today()
                a.motiu_bloqueig = u'No sol·licitat'
                a.tutors_volen_rebre_correu = False                    
            else:
                a.correu_relacio_familia_pare         = alumneDadesAnteriors.correu_relacio_familia_pare
                a.correu_relacio_familia_mare         = alumneDadesAnteriors.correu_relacio_familia_mare
                a.motiu_bloqueig                      = alumneDadesAnteriors.motiu_bloqueig
                a.relacio_familia_darrera_notificacio = alumneDadesAnteriors.relacio_familia_darrera_notificacio
                a.periodicitat_faltes                 = alumneDadesAnteriors.periodicitat_faltes
                a.periodicitat_incidencies            = alumneDadesAnteriors.periodicitat_incidencies
        
        a.save()
    
    #
    # Baixes:
    #
        
    #Els alumnes que hagin quedat a PRC és que s'han donat de baixa:
    AlumnesDonatsDeBaixa = Alumne.objects.filter( estat_sincronitzacio__exact = 'PRC' )
    AlumnesDonatsDeBaixa.update( 
                            data_baixa = date.today(), 
                            estat_sincronitzacio = 'DEL' ,
                            motiu_bloqueig = 'Baixa'                            
                            )

    #Avisar als professors: Baixes
    #: enviar un missatge a tots els professors que tenen aquell alumne.    
    info_nAlumnesEsborrats = len(  AlumnesDonatsDeBaixa )
    professorsNotificar = {}
    for alumneDonatDeBaixa in AlumnesDonatsDeBaixa:
        for professor in Professor.objects.filter(  horari__impartir__controlassistencia__alumne = alumneDonatDeBaixa ).distinct():
            professorsNotificar.setdefault( professor.pk, []  ).append( alumneDonatDeBaixa )
    for professorPK, alumnes in professorsNotificar.items():
        llista = []
        for alumne in alumnes:
            llista.append( u'{0} ({1})'.format(unicode( alumne), alumne.grup.descripcio_grup ) )
        msg = Missatge( remitent = user, text_missatge = u'''El següents alumnes han estat donats de baixa.'''  )
        msg.afegeix_infos( llista )
        msg.envia_a_usuari( Professor.objects.get( pk = professorPK ) , 'IN')
        info_nMissatgesEnviats += 1

    #Avisar als professors: Canvi de grup
    #enviar un missatge a tots els professors que tenen aquell alumne.
    #Només s'executarà el següent bloc de codi
    #  si settings.CUSTOM_PERIODE_CREAR_O_MODIFICAR_INCIDENCIA==True,
    #  perquè, degut a una instrucció if anterior,
    #  no hi hauran alumnes a AlumnesCanviatsDeGrup si és False.   
    info_nAlumnesCanviasDeGrup = len(  AlumnesCanviatsDeGrup )    
    professorsNotificar = {}
    for alumneCanviatDeGrup in AlumnesCanviatsDeGrup:
        qElTenenALHorari = Q( horari__impartir__controlassistencia__alumne = alumneCanviatDeGrup   )
        qImparteixDocenciaAlNouGrup = Q(  horari__grup =  alumneCanviatDeGrup.grup )
        for professor in Professor.objects.filter( qElTenenALHorari | qImparteixDocenciaAlNouGrup  ).distinct():
            professorsNotificar.setdefault( professor.pk, []  ).append( alumneCanviatDeGrup )
    for professorPK, alumnes in professorsNotificar.items():
        llista = []
        for alumne in alumnes:
            llista.append( u'{0} passa a grup {1}'.format(unicode( alumne), alumne.grup.descripcio_grup ) )
        msg = Missatge( remitent = user, text_missatge = u'''El següents alumnes han estat canviats de grup.'''  )
        msg.afegeix_infos( llista )
        msg.envia_a_usuari( Professor.objects.get( pk = professorPK ) , 'IN')
        info_nMissatgesEnviats += 1

    #Avisar als professors: Altes
    #enviar un missatge a tots els professors que tenen aquell alumne.
    professorsNotificar = {}
    for alumneNou in AlumnesInsertats:
        qImparteixDocenciaAlNouGrup = Q(  horari__grup =  alumneNou.grup )
        for professor in Professor.objects.filter( qImparteixDocenciaAlNouGrup ).distinct():
            professorsNotificar.setdefault( professor.pk, []  ).append( alumneNou )
    for professorPK, alumnes in professorsNotificar.items():
        llista = []
        for alumne in alumnes:
            llista.append( u'{0} al grup {1}'.format(unicode( alumne), alumne.grup.descripcio_grup ) )
        msg = Missatge( remitent = user, text_missatge = u'''El següents alumnes han estat donats d'alta.'''  )
        msg.afegeix_infos( llista )
        msg.envia_a_usuari( Professor.objects.get( pk = professorPK ) , 'IN')
        info_nMissatgesEnviats += 1
        
        
    #Treure'ls de les classes: les baixes
    ControlAssistencia.objects.filter( 
                impartir__dia_impartir__gte = date.today(), 
                alumne__in = AlumnesDonatsDeBaixa ).delete()

    #Treure'ls de les classes: els canvis de grup
    ControlAssistencia.objects.filter( 
                impartir__dia_impartir__gte = date.today(), 
                alumne__in = AlumnesCanviatsDeGrup ).delete()

    
    #Altes: posar-ho als controls d'assistència de les classes (?????????)
    
    
    #
    # FI
    #

    Alumne.objects.exclude( estat_sincronitzacio__exact = 'DEL' ).update( estat_sincronitzacio = '')
    errors.append( u'%d alumnes sense grup'%errors_nAlumnesSenseGrup )
    warnings= [  ]
    infos=    [   ]
    infos.append(u'{0} alumnes llegits'.format(info_nAlumnesLlegits) )
    infos.append(u'{0} alumnes insertats'.format(info_nAlumnesInsertats) )
    infos.append(u'{0} alumnes esborrats'.format(info_nAlumnesEsborrats ) )
    infos.append(u'{0} alumnes canviats de grup'.format(info_nAlumnesCanviasDeGrup ) )
    infos.append(u'{0} missatges enviats'.format(info_nMissatgesEnviats ) )

    msg = Missatge( 
                remitent= user, 
                text_missatge = u"Importació Saga finalitzada.")    
    msg.afegeix_errors( errors.sort() )
    msg.afegeix_warnings(warnings)
    msg.afegeix_infos(infos)    
    importancia = 'VI' if len( errors )> 0 else 'IN'
    grupDireccio =  Group.objects.get( name = 'direcció' )
    msg.envia_a_grup( grupDireccio , importancia=importancia)
    
    return { 'errors': errors, 'warnings': warnings, 'infos': infos }

    


def comprovar_grups( f ):

    dialect = csv.Sniffer().sniff(f.readline())
    f.seek(0)
    f.readline()
    f.seek(0)
    reader = csv.DictReader(f, dialect=dialect )
    
    errors=[]
    warnings=[]
    infos=[]
    
    grup_field = next( x for x in reader.fieldnames if x.endswith("_GRUPSCLASSE") )

    if grup_field is None:
        errors.append(u"No trobat el grup classe al fitxer d'importació")
        return False, { 'errors': errors, 'warnings': warnings, 'infos': infos }
    
    for row in reader:
        grup_classe =  unicode(row[grup_field],'iso-8859-1')
        _, new = Grup2Aula.objects.get_or_create( grup_saga = grup_classe )
        if new:
            errors.append( u"El grup '{grup_classe}' del Saga no té correspondència al programa. Revisa les correspondències Saga-Aula".format( grup_classe=grup_classe ) )

    return { 'errors': errors, 'warnings': warnings, 'infos': infos }
            
    


        
    
    
    
