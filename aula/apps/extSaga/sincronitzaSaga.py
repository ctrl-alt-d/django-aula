# This Python file uses the following encoding: utf-8

#--
from aula.apps.alumnes.models import Alumne, Grup, Nivell
from aula.apps.alumnes.tools import markers_disponibles, set_aruco_marker
from aula.apps.missatgeria.missatges_a_usuaris import ALUMNES_DONATS_DE_BAIXA, tipusMissatge, ALUMNES_CANVIATS_DE_GRUP, \
    ALUMNES_DONATS_DALTA, IMPORTACIO_SAGA_FINALITZADA
from aula.apps.presencia.models import ControlAssistencia
from aula.apps.missatgeria.models import Missatge
from aula.apps.usuaris.models import Professor
from aula.apps.extSaga.models import ParametreSaga
from aula.apps.relacioFamilies.tools import creaResponsables

from django.db.models import Q

from datetime import datetime, date
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

def posarDada(dada, text):
    if type(dada)==list:
        for d in dada:
            text=posarDada(d, text)
    elif dada not in text:
        if bool(text):
            text = ', '.join([text] + [dada])
        else:
            text = dada
    return text

def sincronitza(f, user = None):

    errors = []
    markers_per_nivell = markers_disponibles()

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
    reader = csv.DictReader(f)
    errors_nAlumnesSenseGrup=0
    info_nAlumnesLlegits=0
    info_nAlumnesInsertats=0
    info_nAlumnesEsborrats=0
    info_nAlumnesCanviasDeGrup=0
    info_nAlumnesModificats=0
    info_nMissatgesEnviats = 0
    info_nResponsablesCreats = 0
    info_nRespSenseDni = 0
    info_nMenorsSenseResp = 0

    AlumnesCanviatsDeGrup = []
    AlumnesInsertats = []

    '''
        '00_IDENTIFICADOR DE L'ALUMNE/A','01_NOM','02_DATA NAIXEMENT','03_RESPONSABLE 1','04_TELÈFON RESP. 1','05_MÒBIL RESP. 1',
        '06_ADREÇA ELECTR. RESP. 1','07_RESPONSABLE 2','08_TELÈFON RESP. 2','09_MÒBIL RESP. 2','10_ADREÇA ELECTR. RESP. 2','11_ADREÇA',
        '12_LOCALITAT','13_MUNICIPI','14_CORREU ELECTRÒNIC','15_ALTRES TELÈFONS','16_CENTRE PROCEDÈNCIA','17_GRUPSCLASSE',
        '18_DOC. IDENTITAT','19_CP',
        '23_PARENTIU RESP. 1','24_DOC. IDENTITAT RESP. 1','25_ADREÇA RESP. 1','26_LOCALITAT RESP. 1','27_MUNICIPI RESP. 1','28_CP RESP. 1',
        '29_PARENTIU RESP. 2','30_DOC. IDENTITAT RESP. 2','31_ADREÇA RESP. 2','32_LOCALITAT RESP. 2','33_MUNICIPI RESP. 2','34_CP RESP. 2',
    '''
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
        a.altres_telefons = ''
        dni = ''
        # Guarda usuaris Responsable
        r1 = {}
        r2 = {}
        #a.tutors = ''

        for columnName, value in iter(row.items()):
            if bool(value) and isinstance(value, str):
                value=value.strip()
            columnName = unicode(columnName,'iso-8859-1')
            uvalue =  unicode(value,'iso-8859-1')
            if columnName.endswith(u"_IDENTIFICADOR DE L'ALUMNE/A"):
                a.ralc=uvalue
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
            if columnName.endswith( u"_CORREU ELECTRÒNIC"):
                a.correu = uvalue
            if columnName.endswith( u"_DATA NAIXEMENT"):
                dia=time.strptime( uvalue,'%d/%m/%Y')
                a.data_neixement = datetime.fromtimestamp(time.mktime(dia)).date()
                trobatDataNeixement = True
            if columnName.endswith( u"_CENTRE PROCEDÈNCIA"):
                a.centre_de_procedencia = uvalue
            if columnName.endswith( u"_LOCALITAT"):
                a.localitat = uvalue
            if columnName.endswith( u"MUNICIPI"):
                a.municipi = uvalue
            if columnName.endswith(u"_TELÈFON RESP. 1" ):
                if "telefon" not in r1: r1["telefon"] = uvalue
                else:
                    a.altres_telefons = posarDada(uvalue, a.altres_telefons)
            if columnName.endswith(u"_MÒBIL RESP. 1" ):
                if "telefon" not in r1: r1["telefon"] = uvalue
                else:
                    anterior = r1["telefon"]
                    r1["telefon"] = uvalue
                    a.altres_telefons = posarDada(anterior, a.altres_telefons)
            if columnName.endswith(u"_TELÈFON RESP. 2" ):
                if "telefon" not in r2: r2["telefon"] = uvalue
                else:
                    a.altres_telefons = posarDada(uvalue, a.altres_telefons)
            if columnName.endswith(u"_MÒBIL RESP. 2" ):
                if "telefon" not in r2: r2["telefon"] = uvalue
                else:
                    anterior = r2["telefon"]
                    r2["telefon"] = uvalue
                    a.altres_telefons = posarDada(anterior, a.altres_telefons)
            if columnName.endswith(u"_ADREÇA ELECTR. RESP. 1" ):
                r1["correu"] = uvalue
            if columnName.endswith(u"_ADREÇA ELECTR. RESP. 2" ):
                r2["correu"] = uvalue
            if columnName.endswith(u"_ALTRES TELÈFONS"):
                a.altres_telefons = posarDada(uvalue, a.altres_telefons)

            if columnName.endswith( u"_ADREÇA" ):
                a.adreca = uvalue
            if columnName.endswith( u"_CP"):
                a.cp = uvalue
            if columnName.endswith( u"_DOC. IDENTITAT"):
                dni = uvalue
            if columnName.endswith( u"_DOC. IDENTITAT RESP. 1"):
                r1["dni"] = uvalue[-10:]
            if columnName.endswith(u"_RESPONSABLE 1" ):
                if len(uvalue.split(','))>1:
                    r1["nom"] = uvalue.split(',')[1].lstrip().rstrip()                #nomes fins a la coma
                    r1["cognoms"] = uvalue.split(',')[0]
                else:
                    r1["nom"] = uvalue.split(',')[0].lstrip().rstrip()                #nomes fins a la coma
                    r1["cognoms"] = ''
            if columnName.endswith( u"_PARENTIU RESP. 1"):
                r1["parentiu"]=uvalue
            if columnName.endswith( u"_ADREÇA RESP. 1" ):
                r1["adreca"]=uvalue
            if columnName.endswith( u"_LOCALITAT RESP. 1"):
                r1["localitat"]=uvalue
            if columnName.endswith( u"_MUNICIPI RESP. 1"):
                r1["municipi"]=uvalue
            if columnName.endswith( u"_CP RESP. 1"):
                r1["cp"]=uvalue
            if columnName.endswith( u"_DOC. IDENTITAT RESP. 2"):
                r2["dni"] = uvalue[-10:]
            if columnName.endswith(u"_RESPONSABLE 2" ):
                if len(uvalue.split(','))>1:
                    r2["nom"] = uvalue.split(',')[1].lstrip().rstrip()                #nomes fins a la coma
                    r2["cognoms"] = uvalue.split(',')[0]
                else:
                    r2["nom"] = uvalue.split(',')[0].lstrip().rstrip()                #nomes fins a la coma
                    r2["cognoms"] = ''
            if columnName.endswith( u"_PARENTIU RESP. 2"):
                r2["parentiu"]=uvalue
            if columnName.endswith( u"_ADREÇA RESP. 2" ):
                r2["adreca"]=uvalue
            if columnName.endswith( u"_LOCALITAT RESP. 2"):
                r2["localitat"]=uvalue
            if columnName.endswith( u"_MUNICIPI RESP. 2"):
                r2["municipi"]=uvalue
            if columnName.endswith( u"_CP RESP. 2"):
                r2["cp"]=uvalue

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
            a.periodicitat_faltes = alumneDadesAnteriors.periodicitat_faltes
            a.periodicitat_incidencies = alumneDadesAnteriors.periodicitat_incidencies
            a.foto = alumneDadesAnteriors.foto
            a.responsable_preferent = alumneDadesAnteriors.responsable_preferent
            a.observacions = alumneDadesAnteriors.observacions
            #el recuperem, havia estat baixa:
            if alumneDadesAnteriors.data_baixa:
                info_nAlumnesInsertats+=1
                info_nAlumnesModificats-=1
                a.data_alta = date.today()
                a.motiu_bloqueig = ""
            else:
                a.data_alta = alumneDadesAnteriors.data_alta
                a.motiu_bloqueig = alumneDadesAnteriors.motiu_bloqueig

        #DEPRECATED vvv
        if alumneDadesAnteriors and alumneDadesAnteriors.correu_relacio_familia_pare:
            r1["correu_relacio_familia"]=alumneDadesAnteriors.correu_relacio_familia_pare
            r1["periodicitat_faltes"]=alumneDadesAnteriors.periodicitat_faltes
            r1["periodicitat_incidencies"]=alumneDadesAnteriors.periodicitat_incidencies
            a.correu_relacio_familia_pare = ''
        if alumneDadesAnteriors and alumneDadesAnteriors.correu_relacio_familia_mare:
            r2["correu_relacio_familia"]=alumneDadesAnteriors.correu_relacio_familia_mare
            r2["periodicitat_faltes"]=alumneDadesAnteriors.periodicitat_faltes
            r2["periodicitat_incidencies"]=alumneDadesAnteriors.periodicitat_incidencies
            a.correu_relacio_familia_mare = ''
        #DEPRECATED ^^^

        set_aruco_marker(a, markers_per_nivell[a.grup.curs.nivell.pk])
        a.save()
        # Crea usuaris Responsable
        err_resp_menors = 0
        if (r1.get("cognoms",None) or r1.get("nom",None)) and not r1.get("dni",None):
            info_nRespSenseDni += 1
            if a.edat()<18: err_resp_menors += 1
        if (r2.get("cognoms",None) or r2.get("nom",None)) and not r2.get("dni",None):
            info_nRespSenseDni += 1
            if a.edat()<18: err_resp_menors += 1
        if err_resp_menors==2: info_nMenorsSenseResp += 1
        info_nResponsablesCreats += creaResponsables(a, [r1, r2])
        cursos.add(a.grup.curs)
        #DEPRECATED vvv
        if alumneDadesAnteriors and not alumneDadesAnteriors.responsable_preferent and alumneDadesAnteriors.responsables.exists():
            r1, r2 = a.get_responsables()
            if alumneDadesAnteriors.primer_responsable==1 and r2: a.responsable_preferent = r2
            else: a.responsable_preferent = r1
            a.save()
        #DEPRECATED ^^^
        
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
    infos.append(u'{0} alumnes modificats'.format(info_nAlumnesModificats ) )
    infos.append(u'{0} alumnes esborrats'.format(info_nAlumnesEsborrats ) )
    infos.append(u'{0} alumnes canviats de grup'.format(info_nAlumnesCanviasDeGrup ) )
    infos.append(u'{0} alumnes en estat sincronització manual'.format( \
        len(Alumne.objects.filter(estat_sincronitzacio__exact = 'MAN'))))
    infos.append(u'{0} missatges enviats'.format(info_nMissatgesEnviats ) )
    infos.append(u'{0} responsables creats'.format(info_nResponsablesCreats ) )
    if info_nRespSenseDni>0: infos.append(u'{0} responsables sense identificació'.format(info_nRespSenseDni ) )
    if info_nMenorsSenseResp>0: infos.append(u'{0} alumnes menors d\'edat sense responsable'.format(info_nMenorsSenseResp ) )
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







    