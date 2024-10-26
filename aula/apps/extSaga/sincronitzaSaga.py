# This Python file uses the following encoding: utf-8

#--
from aula.apps.alumnes.models import Alumne, Grup, Nivell
from aula.apps.missatgeria.missatges_a_usuaris import ALUMNES_DONATS_DE_BAIXA, tipusMissatge, ALUMNES_CANVIATS_DE_GRUP, \
    ALUMNES_DONATS_DALTA, IMPORTACIO_SAGA_FINALITZADA
from aula.apps.presencia.models import ControlAssistencia
from aula.apps.missatgeria.models import Missatge
from aula.apps.usuaris.models import Professor
from aula.apps.extSaga.models import ParametreSaga
from aula.apps.relacioFamilies.tools import creaResponsables

from django.db.models import Q

from datetime import date
from django.contrib.auth.models import Group

import csv, time
from aula.apps.extSaga.models import Grup2Aula

from django.conf import settings

from aula.utils.tools import unicode

def autoRalc(ident):
    '''
    Calcula Ralc per a alumnes que no tenen.
    ident identificador de l'alumne, normalment DNI
    Utilitza el paràmetre autoRalc de paràmetres Saga, crea un identificador 
    format per parametre + ident
    Retorna el ralc calculat 
    '''
    autoRalc, _ = ParametreSaga.objects.get_or_create( nom_parametre = 'autoRalc' )
    if bool(autoRalc.valor_parametre):
        ralc= autoRalc.valor_parametre + ident[-9:]
        return ralc
    return ident

def sincronitza(f, user = None):

    errors = []

    try:
        msgs = comprovar_grups( f )
    
        if msgs["errors"]:
            return msgs
    except:
        errors.append('Fitxer incorrecte')
        return {'errors': errors, 'warnings': [], 'infos': []}

    #Exclou els alumnes AMB esborrat i amb estat MAN (creats manualment)
    Alumne.objects.exclude( estat_sincronitzacio__exact = 'DEL' ).exclude( estat_sincronitzacio__exact = 'MAN') \
        .update( estat_sincronitzacio = 'PRC')
        #,"00_IDENTIFICADOR DE L'ALUMNE/A","01_NOM","02_ADRE�A","03_CP","04_CENTRE PROCED�NCIA","05_CODI LOCALITAT","06_CORREU ELECTR�NIC","07_DATA NAIXEMENT","08_DOC. IDENTITAT","09_GRUPSCLASSE","10_NOM LOCALITAT","11_TEL�FONS","12_TUTOR(S)"
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

 #,"00_IDENTIFICADOR DE L'ALUMNE/A","01_NOM","02_DATA NAIXEMENT",
 #"03_ADREÇA","04_CENTRE PROCEDÈNCIA","05_GRUPSCLASSE","06_CORREU ELECTRÒNIC","07_LOCALITAT",
 #"08_TELÈFON RESP. 1","09_TELÈFON RESP. 2","10_RESPONSABLE 2","11_RESPONSABLE 1"

    trobatGrupClasse = False
    trobatNom = False
    trobatDataNeixement = False
    trobatRalc = False

    f.seek(0)
    cursos = set()
    for row in reader:
        info_nAlumnesLlegits+=1
        a=Alumne()
        a.ralc = ''
        a.telefons = ''
        dni = ''
        # Guarda usuaris Responsable
        # Es tracta d'una modificació provisional per a poder fer proves
        resp1 = {}
        resp2 = {}
        #a.tutors = ''
        #a.correu_tutors = ''

        for columnName, value in iter(row.items()):
            if bool(value) and isinstance(value, str):
                value=value.strip()
            columnName = unicode(columnName,'iso-8859-1')
            #columnName = unicode( rawColumnName, 'iso-8859-1'  )
            uvalue =  unicode(value,'iso-8859-1')
            if columnName.endswith(u"_IDENTIFICADOR DE L'ALUMNE/A"):
                a.ralc=unicode(value,'iso-8859-1')
                trobatRalc = True
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
            #if columnName.endswith( u"_CORREU ELECTRÒNIC")  or columnName.find( u"_ADREÇA ELECTR. RESP.")>=0 :
            #    a.correu_tutors += unicode(value,'iso-8859-1') + u', '
            if columnName.endswith( u"_CORREU ELECTRÒNIC"):
                a.correu = unicode(value,'iso-8859-1')
            if columnName.endswith( u"_DATA NAIXEMENT"):
                dia=time.strptime( unicode(value,'iso-8859-1'),'%d/%m/%Y')
                a.data_neixement = time.strftime('%Y-%m-%d', dia)
                trobatDataNeixement = True
            if columnName.endswith( u"_CENTRE PROCEDÈNCIA"):
                a.centre_de_procedencia = unicode(value,'iso-8859-1')
            if columnName.endswith( u"_LOCALITAT"):
                a.localitat = unicode(value,'iso-8859-1')
                resp1["localitat"]=a.localitat
                resp2["localitat"]=a.localitat
            if columnName.endswith( u"MUNICIPI"):
                a.municipi = unicode(value,'iso-8859-1')
                resp1["municipi"]=a.municipi
                resp2["municipi"]=a.municipi
            # if columnName.find( u"_TELÈFON RESP")>=0 or columnName.find( u"_MÒBIL RESP")>=0 or columnName.find( u"_ALTRES TELÈFONS")>=0 :
            #     a.telefons += unicode(value,'iso-8859-1') + u', '
            if columnName.endswith(u"_TELÈFON RESP. 1" ):
                if "telefon" not in resp1: resp1["telefon"] = unicode(value,'iso-8859-1')
            if columnName.endswith(u"_TELÈFON RESP. 2" ):
                if "telefon" not in resp2: resp2["telefon"] = unicode(value,'iso-8859-1')
            if columnName.endswith(u"_MÒBIL RESP. 1" ):
                resp1["telefon"] = unicode(value,'iso-8859-1')
            if columnName.endswith(u"_MÒBIL RESP. 2" ):
                resp2["telefon"] = unicode(value,'iso-8859-1')
            if columnName.endswith(u"_ADREÇA ELECTR. RESP. 1" ):
                resp1["correu"] = unicode(value,'iso-8859-1')
            if columnName.endswith(u"_ADREÇA ELECTR. RESP. 2" ):
                resp2["correu"] = unicode(value,'iso-8859-1')
            if columnName.endswith(u"_ALTRES TELÈFONS"):
                a.altres_telefons = unicode(value, 'iso-8859-1')

            # if columnName.find( u"_RESPONSABLE")>=0:
            #     a.tutors = unicode(value,'iso-8859-1') + u', '
            if columnName.endswith(u"_RESPONSABLE 1" ):
                resp1["nom"] = unicode(value,'iso-8859-1')
            if columnName.endswith(u"_RESPONSABLE 2" ):
                resp2["nom"] = unicode(value,'iso-8859-1')
            if columnName.endswith( u"_ADREÇA" ):
                a.adreca = unicode(value,'iso-8859-1')
                resp1["adreca"]=a.adreca
                resp2["adreca"]=a.adreca
            if columnName.endswith( u"_CP"):
                a.cp = unicode(value,'iso-8859-1')
                resp1["cp"]=a.cp
                resp2["cp"]=a.cp
            if columnName.endswith( u"_DOC. IDENTITAT"):
                dni = unicode(value,'iso-8859-1')
            if columnName.endswith( u"_DOC. IDENTITAT RESP. 1"):
                resp1["dni"] = unicode(value,'iso-8859-1')[-9:]
            if columnName.endswith( u"_DOC. IDENTITAT RESP. 2"):
                resp2["dni"] = unicode(value,'iso-8859-1')[-9:]


        if not (trobatGrupClasse and trobatNom and trobatDataNeixement and trobatRalc):
            return { 'errors': [ u'Falten camps al fitxer' ], 'warnings': [], 'infos': [] }


        alumneDadesAnteriors = None
        if not bool(a.ralc) or a.ralc=='':
            a.ralc=autoRalc(dni)

        try:
            q_mateix_ralc = Q( ralc = a.ralc ) # & Q(  grup__curs__nivell = a.grup.curs.nivell )

            # Antic mètode de cassar alumnes:
            #
            # q_mateix_cognom = Q(
            #                 cognoms = a.cognoms )
            # q_mateix_nom = Q(
            #                 nom = a.nom,
            #                   )
            # q_mateix_neixement = Q(
            #                 data_neixement = a.data_neixement
            #                     )
            # q_mateixa_altres = Q(
            #                 adreca = a.adreca,
            #                 telefons = a.telefons,
            #                 localitat = a.localitat,
            #                 centre_de_procedencia = a.centre_de_procedencia,
            #                 adreca__gte= u""
            #                     )
            #
            # condicio1 = q_mateix_nom & q_mateix_cognom & q_mateix_neixement
            # condicio2 = q_mateix_nom & q_mateix_cognom & q_mateixa_altres
            # condicio3 = q_mateix_nom & q_mateixa_altres & q_mateix_neixement
            #
            #
            # alumneDadesAnteriors = Alumne.objects.get(
            #                                 condicio1 | condicio2 | condicio3
            #                                   )

            alumneDadesAnteriors =Alumne.objects.get (q_mateix_ralc)

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
            a.nom_sentit = alumneDadesAnteriors.nom_sentit
            info_nAlumnesModificats+=1

            # En cas que l'alumne pertanyi a un dels grups parametritzat com a estàtic,
            # no se li canviarà de grup en les importacions de SAGA.
            grups_estatics, _ = ParametreSaga.objects.get_or_create( nom_parametre = 'grups estatics' )
            es_de_grup_estatic = False
            for prefixe_grup in grups_estatics.valor_parametre.split(','):
                prefix = prefixe_grup.replace(' ','')
                if prefix:
                    es_de_grup_estatic = es_de_grup_estatic or alumneDadesAnteriors.grup.descripcio_grup.startswith( prefix )

            if a.grup.pk != alumneDadesAnteriors.grup.pk:
                if es_de_grup_estatic: #no canviar-li de grup
                    a.grup = alumneDadesAnteriors.grup
                else:
                    AlumnesCanviatsDeGrup.append(a)

            a.user_associat = alumneDadesAnteriors.user_associat
            a.usuaris_app_associats.set(alumneDadesAnteriors.usuaris_app_associats.all())
            a.correu_relacio_familia_pare = alumneDadesAnteriors.correu_relacio_familia_pare
            a.correu_relacio_familia_mare = alumneDadesAnteriors.correu_relacio_familia_mare
            a.relacio_familia_darrera_notificacio = alumneDadesAnteriors.relacio_familia_darrera_notificacio
            a.periodicitat_faltes = alumneDadesAnteriors.periodicitat_faltes
            a.periodicitat_incidencies = alumneDadesAnteriors.periodicitat_incidencies
            a.tutors_volen_rebre_correu = alumneDadesAnteriors.tutors_volen_rebre_correu = False
            a.foto = alumneDadesAnteriors.foto
            a.primer_responsable = alumneDadesAnteriors.primer_responsable
            a.observacions = alumneDadesAnteriors.observacions
             #el recuperem, havia estat baixa:
            if alumneDadesAnteriors.data_baixa:
                info_nAlumnesInsertats+=1
                a.data_alta = date.today()
                a.motiu_bloqueig = ""
            else:
                a.data_alta = alumneDadesAnteriors.data_alta
                a.motiu_bloqueig = alumneDadesAnteriors.motiu_bloqueig

        a.save()
        # Crea usuaris Responsable
        # Es tracta d'una modificació provisional per a poder fer proves
        creaResponsables(a, [resp1, resp2])
        cursos.add(a.grup.curs)
    #
    # Baixes:
    #

    # Els alumnes d'Esfer@ no s'han de tenir en compte per fer les baixes
    AlumnesDeEsfera = Alumne.objects.exclude(grup__curs__in=cursos)
    # Es canvia estat PRC a ''. No modifica DEL ni MAN
    AlumnesDeEsfera.filter( estat_sincronitzacio__exact = 'PRC' ).update(estat_sincronitzacio='')
    
    # amorilla@xtec.cat
    #Per solucionar el conflicte de cursos compartits Esfer@-SAGA:
    #Es pot definir, a Extsaga / Paràmetres Saga, un paràmetre 'CursosManuals' amb la llista de cursos en què els alumnes quedaran insertats com a MAN
    #Aquesta llista inclou els noms dels cursos, segons el camp 'nom_curs'. p.ex: ['1'], ['1', '2'], ['2', '4'], ...
    #Si existeix la llista, manté els alumnes afegits d'aquests cursos en estat 'MAN', així la importació des d'esfer@ no donarà de baixa els alumnes
    #Si no hi ha llista (o no existeix el paràmetre) es comporta com sempre, no els marca 'MAN' i dona de baixa els alumnes que no surten al fitxer
    CursosManuals, _ = ParametreSaga.objects.get_or_create( nom_parametre = 'CursosManuals' )
    if bool(CursosManuals.valor_parametre):
        try:
            CursosManuals=eval(CursosManuals.valor_parametre)
            if not isinstance(CursosManuals, list):
                CursosManuals=list(CursosManuals)
        except:
            CursosManuals=[]
    else:
        CursosManuals=[]
    #Els alumnes que hagin quedat a PRC és que s'han donat de baixa, excepte els que corresponen a cursos manuals
    AlumnesDonatsDeBaixa = Alumne.objects.filter( estat_sincronitzacio__exact = 'PRC' ).exclude(grup__curs__nom_curs__in= CursosManuals)
    AlumnesDonatsDeBaixa.update(
                            data_baixa = date.today(),
                            estat_sincronitzacio = 'DEL' ,
                            motiu_bloqueig = 'Baixa'
                            )
    if bool(CursosManuals) and len(CursosManuals)>0:
        #Hi ha una llista de cursos a on els alumnes han de quedar Manuals.
        Alumne.objects.filter( Q(estat_sincronitzacio__exact = 'S-I') | Q(estat_sincronitzacio__exact = 'S-U'),
                               grup__curs__nom_curs__in= CursosManuals).update(estat_sincronitzacio = 'MAN', motiu_bloqueig = '')

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
        missatge = ALUMNES_DONATS_DE_BAIXA
        tipus_de_missatge = tipusMissatge(missatge)
        msg = Missatge( remitent = user, text_missatge = missatge, tipus_de_missatge = tipus_de_missatge  )
        msg.afegeix_infos( llista )
        msg.envia_a_usuari( Professor.objects.get( pk = professorPK ) , 'IN')
        info_nMissatgesEnviats += 1

    #Avisar als professors: Canvi de grup
    #enviar un missatge a tots els professors que tenen aquell alumne.
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
        missatge = ALUMNES_CANVIATS_DE_GRUP
        tipus_de_missatge = tipusMissatge(missatge)
        msg = Missatge( remitent = user, text_missatge = missatge,tipus_de_missatge = tipus_de_missatge  )
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
        missatge = ALUMNES_DONATS_DALTA
        tipus_de_missatge = tipusMissatge(missatge)
        msg = Missatge( remitent = user, text_missatge = missatge, tipus_de_missatge = tipus_de_missatge  )
        msg.afegeix_infos( llista )
        msg.envia_a_usuari( Professor.objects.get( pk = professorPK ) , 'IN')
        info_nMissatgesEnviats += 1


    #Treure'ls de les classes: les baixes
    ControlAssistencia.objects.filter(
                impartir__dia_impartir__gte = date.today(),
                alumne__in = AlumnesDonatsDeBaixa ).delete()

    #Treure'ls de les classes: els canvis de grup   #Todo: només si l'àmbit és grup.

    ambit_no_es_el_grup = Q( impartir__horari__assignatura__tipus_assignatura__ambit_on_prendre_alumnes__in = [ 'C', 'N', 'I' ] )
    ( ControlAssistencia
      .objects
      .filter( ambit_no_es_el_grup )
      .filter( impartir__dia_impartir__gte = date.today() )
      .filter( alumne__in = AlumnesCanviatsDeGrup )
      .delete()
     )


    #Altes: posar-ho als controls d'assistència de les classes (?????????)


    #
    # FI
    #
    # Tornem a l'estat de sincronització en blanc, excepte els alumnes esborrats DEL i els alumnes entrats manualment MAN.
    Alumne.objects.exclude( estat_sincronitzacio__exact = 'DEL' ).exclude( estat_sincronitzacio__exact = 'MAN') \
        .update( estat_sincronitzacio = '')
    errors.append( u'%d alumnes sense grup'%errors_nAlumnesSenseGrup )
    warnings= [  ]
    infos=    [   ]
    infos.append(u'{0} alumnes llegits'.format(info_nAlumnesLlegits) )
    infos.append(u'{0} alumnes insertats'.format(info_nAlumnesInsertats) )
    infos.append(u'{0} alumnes esborrats'.format(info_nAlumnesEsborrats ) )
    infos.append(u'{0} alumnes canviats de grup'.format(info_nAlumnesCanviasDeGrup ) )
    infos.append(u'{0} alumnes en estat sincronització manual'.format( \
        len(Alumne.objects.filter(estat_sincronitzacio__exact = 'MAN'))))
    infos.append(u'{0} missatges enviats'.format(info_nMissatgesEnviats ) )
    missatge = IMPORTACIO_SAGA_FINALITZADA
    tipus_de_missatge = tipusMissatge(missatge)
    msg = Missatge(
                remitent= user,
                text_missatge = missatge,
                tipus_de_missatge = tipus_de_missatge)
    msg.afegeix_errors( errors )
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
        grup_classe =  unicode(row[grup_field],'iso-8859-1').strip()
        _, new = Grup2Aula.objects.get_or_create( grup_saga = grup_classe )
        if new:
            errors.append( u"El grup '{grup_classe}' del Saga no té correspondència al programa. Revisa les correspondències Saga-Aula".format( grup_classe=grup_classe ) )

    return { 'errors': errors, 'warnings': warnings, 'infos': infos }







    