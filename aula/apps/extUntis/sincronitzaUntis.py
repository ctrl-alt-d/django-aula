from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from aula.apps.missatgeria.missatges_a_usuaris import RECORDA_REPROGRAMAR_CLASSES, tipusMissatge
from aula.apps.usuaris.models import Professor
from aula.apps.horaris.models import Horari, DiaDeLaSetmana, FranjaHoraria, Festiu
'''
amorilla@xtec.cat
Faig servir els mateixos paràmetres del Kronowin
TODO Crec que es podrien unificar tots els paràmetres d'importació de dades (saga,esfera,horaris,...)
'''
from aula.apps.extKronowin.models import ParametreKronowin
from aula.apps.assignatures.models import Assignatura, TipusDAssignatura
from aula.apps.aules.models import Aula
import traceback

from aula.apps.extUntis.models import Agrupament
from aula.apps.alumnes.models import Nivell, Grup, Curs
import xmltodict
import datetime

def esGrupAlumnes(nomgrup, senseGrups):
    """Detecta si és grup d'alumnes o no.  
    
    nomgrup  nom del grup que tenim
        xxxxNA   nivell xxxx  curs N  grup A
        xxxxNAN  nivell xxxx  curs N  grup A  subgrp N
    senseGrups  indica que s'admeten grups sense lletra ('-')
    Retorna True, nivell, curs, grup
    o    False, None, None, None
        
    """
    
    if len(nomgrup)<3:
        return False, None, None, None
    n=nomgrup[:len(nomgrup)-2]
    c=nomgrup[len(nomgrup)-2]
    g=nomgrup[len(nomgrup)-1]
    if (c.isdigit() and g.isalpha()):
        #    xxxxNA   nivell xxxx  curs N  grup A
        return True, n, c, g
    if (c.isalpha()) and len(nomgrup)>=4:
        n=nomgrup[:len(nomgrup)-3]
        c=nomgrup[len(nomgrup)-3]
        g=nomgrup[len(nomgrup)-2]
        sg=nomgrup[len(nomgrup)-1]
        if (c.isdigit() and g.isalpha() and sg.isdigit()):
            #    xxxxNAN  nivell xxxx  curs N  grup AN
            return True, n, c, g+sg
    if senseGrups:
        n=nomgrup[:len(nomgrup)-2]
        c=nomgrup[len(nomgrup)-2] 
        g=nomgrup[len(nomgrup)-1]
        if (c.isdigit() and g=='-'):
            #    xxxxN  nivell xxxx  curs N
            return True, n, c, '-'       
    return False, None, None, None

def creaAgrupaments(gruph, llista, di, df, senseGrups):
    """Crea els agrupaments necessaris
    
    gruph correspon al grup virtual dels horaris Ex: <ESO1ABC>
    llista correspon a la llistra d'Untis dels diversos grups que aporten alumnes
             Ex: 'CL_ESO1A CL_ESO1B CL_ESO1C'
    di data inici del curs
    df data fi del curs
    senseGrups  indica que s'admeten grups sense lletra
    retorna warnings
    
    """
    
    warnings=[]
    # Per cada grup de la llista farà un agrupament
    for nomg in llista:
        nomg=nomg[3:]
        galum, n, c, g = esGrupAlumnes(nomg,senseGrups)

        if (galum):
            # Si és un grup d'alumnes el crea
            grupnomg, warn=creaGrup(n,c,g,di,df)
            warnings.extend(warn)  
        else:
            warnings.append(u'No es crea Agrupament, grup erroni: \'%s\' --> \'%s\'' % (nomg, str(gruph)) )
            continue

        c_agrup=Agrupament.objects.filter(grup_alumnes=grupnomg, grup_horari=gruph)
        if not c_agrup.exists():
            agrup=Agrupament.objects.create(grup_alumnes=grupnomg, grup_horari=gruph)
            agrup.save()
            warnings.append(u'Nou agrupament: \'%s\'' % (agrup))
            
    return warnings

def fusionaGrups(llgrup, di, df, senseGrups):
    """Fusiona els noms dels grups en cas de desdoblament.
    
    llgrup correspon a la llistra d'Untis dels diversos grups que aporten alumnes
    di data inici del curs
    df data fi del curs
    Crea el grup i determina el tipus d'assignatura ('G', 'A', 'AN')
    Crea els agrupaments necessaris
    Exemples d'entrada i sortides:
    'CL_ESO1A CL_ESO1B CL_ESO1C' -->  <ESO1ABC>  tipus 'A'
    'CL_SMX1A1 CL_SMX1A2' -->  <SMX1A12>  tipus 'AN'
    'CL_BAT1A CL_BAT2A' -->  <BAT1A2A>  tipus 'A'
    'CL_ACO1A' -->  <ACO1A>  tipus 'G'
    'CL_DAW1A CL_ASX1A' -->  <ASX1ADAW1A>  tipus 'A'
             ASX1A --> ASX1ADAW1A 
             DAW1A --> ASX1ADAW1A
    
    Retorna el grup, tipus i warnings
    
    """
    
    warnings=[]
    
    llista=sorted(llgrup.split())
    if len(llista)<=1:
        ng=llgrup[3:]
        tipus='G'
        galum, n, c, g = esGrupAlumnes(ng,senseGrups)
        if not galum:
            return None, tipus, warnings
        gruph, _ = creaGrup(n,c,g,di,df)
        #  si el grup surt a Agrupaments --> tipus 'A'
        agrup=Agrupament.objects.filter(grup_horari=gruph)
        if agrup.exists():
            tipus='A'
        # Es tracta de cicles ?
        try:
            if Nivell.objects.get(nom_nivell=n).getNivellCustom()=='CICLES':
                if tipus=='A':
                    tipus='AN'
                else:
                    tipus='N'
        except ObjectDoesNotExist:
            pass
        return gruph, tipus, warnings
    else:
        # Comprova si corresponen al mateix nivell i curs
        prefixe=llista[0][3:len(llista[0])-1]
        fusio=True
        grups=''
        for g in llista:
            pre=g[3:len(g)-1]
            if (pre!=prefixe):
                fusio=False
                break
            grups=grups+g[len(g)-1]
        if fusio:
            # nivell i curs definits
            n=prefixe[:len(prefixe)-1]
            c=prefixe[len(prefixe)-1]
            if (c.isdigit()):
                # 'CL_ESO1A CL_ESO1B CL_ESO1C' -->  'ESO1ABC'
                g=grups
                grupc, warn=creaGrup(n,c,g,di,df)
                warnings.extend(warn)  
                warn=creaAgrupaments(grupc, llista, di, df, senseGrups)
                warnings.extend(warn)  
                tipus='A'
                # Es tracta de cicles ?
                try:
                    if Nivell.objects.get(nom_nivell=n).getNivellCustom()=='CICLES':
                        tipus='AN'
                except ObjectDoesNotExist:
                    pass
                return grupc, tipus, warnings
            else:
                # 'CL_SMX1A1 CL_SMX1A2' -->  'SMX1A12'
                n=prefixe[:len(prefixe)-2]
                c=prefixe[len(prefixe)-2]
                g=prefixe[len(prefixe)-1]+grups
                grupc, warn=creaGrup(n,c,g,di,df)
                warnings.extend(warn)  
                warn=creaAgrupaments(grupc, llista, di, df, senseGrups)
                warnings.extend(warn)  
                tipus='A'
                # Es tracta de cicles ?
                try:
                    if Nivell.objects.get(nom_nivell=n).getNivellCustom()=='CICLES':
                        tipus='AN'
                except ObjectDoesNotExist:
                    pass                
                return grupc, tipus, warnings
        else:
            #Grupsubgrup o cursos diferents
            prefixe=llista[0][3:len(llista[0])-2]
            fusio=True
            grups=''
            for g in llista:
                pre=g[3:len(g)-2]
                if (pre!=prefixe):
                    fusio=False
                    break
                grups=grups+g[len(g)-2:]
            if fusio:
                # nivell
                n=prefixe
                # Es faran agrupaments
                # 'CL_SMX1A1 CL_SMX1B1' -->  'SMX1A1B1'
                # 'CL_BAT1A CL_BAT2A' -->  'BAT1A2A'
                g=grups
                grupc, warn=creaGrup(n,'-',g,di,df)
                warnings.extend(warn)  
                # Es faran agrupaments
                warn=creaAgrupaments(grupc, llista, di, df, senseGrups)
                warnings.extend(warn)  
                tipus='A'
                # Es tracta de cicles ?
                try:
                    if Nivell.objects.get(nom_nivell=n).getNivellCustom()=='CICLES':
                        tipus='AN'
                except ObjectDoesNotExist:
                    pass
                return grupc, tipus, warnings            

            grups=''
            for g in llista:
                grups=grups+g[3:]
            grupc, warn=creaGrup('ALL','1',grups,di,df)
            warnings.extend(warn)  
            # Es faran agrupaments 
            warn=creaAgrupaments(grupc, llista, di, df, senseGrups)
            warnings.extend(warn)  
            tipus='A'
            return grupc, tipus, warnings

def creaGrup(n, c, g, di, df):
    '''
    Crea el grup.

    n nivell
    c curs
    g grup (i subgrup)
    di data inici del curs
    df data fi del curs
    retorna warnings
    
    '''
    
    warnings = []
    # Grup d'alumnes
    nivell=None
    if n is not None:
        nivell, nnivell=Nivell.objects.get_or_create(nom_nivell=n)
        if (nnivell):
            nivell.descripcio_nivell=n
            nivell.save()
            warnings.append(u'Nou nivell: \'%s\'' % (nivell))
    curs=None
    if c is not None:
        curs, ncurs=Curs.objects.get_or_create(nivell=nivell, nom_curs=c)
        if di is not None:
            if curs.data_inici_curs is None or (curs.data_inici_curs<di or curs.data_inici_curs>df ): 
                curs.data_inici_curs=di
        if df is not None:
            if curs.data_fi_curs is None or (curs.data_fi_curs<di or curs.data_fi_curs>df ): 
                curs.data_fi_curs=df
        if (ncurs):
            curs.nom_curs=c
            curs.nom_curs_complert=(n+"-"+c) if c !='-' else (n+"-") 
            warnings.append(u'Nou curs: \'%s\'' % (curs))
        curs.save()
    
    grup, ngrup=Grup.objects.get_or_create(curs=curs, nom_grup=g)
    if (ngrup):
        if (n!='ALL' or g=='-') and c!='-':
            grup.descripcio_grup=n+c+g
        else:
            if c=='-':
                grup.descripcio_grup=n+g
            else:
                grup.descripcio_grup=g
        warnings.append(u'Nou grup: \'%s\'' % (grup))
        grup.save()

    return grup, warnings

def sincronitza(xml, usuari):
    '''
    Importa dades del fitxer xml d'Untis.
    
    retorna missatges: errors, warnings, informatius
    '''
    
    _, _ = Group.objects.get_or_create(name=u'direcció')
    grupProfessors, _ = Group.objects.get_or_create(name='professors')
    grupProfessionals, _ = Group.objects.get_or_create(name='professional')

    errors = []
    warnings = []
    infos = []
    
    try:
        dades=xmltodict.parse(xml)
    except:
        errors.append('Fitxer incorrecte')
        return {'errors': errors, 'warnings': warnings, 'infos': infos}

    if not ('document' in dades) or not dades['document']:
        errors.append('Fitxer incorrecte')
        return {'errors': errors, 'warnings': warnings, 'infos': infos}
    
    nLiniesLlegides = 0
    nHorarisModificats = 0
    nAulesCreades = 0
    nAssignaturesCreades = 0
    
    #  Només en desenvolupament
    #  Utilitza el paràmetre que indica si es treballa senseGrups
    #  Si 'True' vol dir que es crean grups addicionals sense lletra, només és necessari si
    #  a principi de curs encara no s'han definit els grups al Saga i Esfera.
    senseGrups, _ = ParametreKronowin.objects.get_or_create(nom_parametre='senseGrups',
                                                                defaults={'valor_parametre': 'False', })
    if senseGrups.valor_parametre == 'True': senseGrups = True
    else: senseGrups = False

    # Dates generals d'inici i final de curs
    inicurs=None
    ficurs=None
    if (('general' in dades['document']) and (dades['document']['general']) and
        ('schoolyearbegindate' in dades['document']['general']) and
        ('schoolyearenddate' in dades['document']['general'])):
        inicurs=dades['document']['general']['schoolyearbegindate']
        if inicurs:
            inicurs=datetime.datetime.strptime(inicurs, '%Y%m%d').date()
        ficurs=dades['document']['general']['schoolyearenddate']
        if ficurs:
            ficurs=datetime.datetime.strptime(ficurs, '%Y%m%d').date()
    
    # Crea els tipus i àmbits si és necessari
    tipus, nou = TipusDAssignatura.objects.get_or_create(tipus_assignatura='Agrupament')
    if nou:
        tipus.ambit_on_prendre_alumnes='A'
    tipus.save()
    tipus, nou = TipusDAssignatura.objects.get_or_create(tipus_assignatura='Agrupament amb nivells')
    if nou:
        tipus.ambit_on_prendre_alumnes='AN'
    tipus.save()
    tipus, nou = TipusDAssignatura.objects.get_or_create(tipus_assignatura='Regular')
    if nou:
        tipus.ambit_on_prendre_alumnes='G'
    tipus.save()
    tipus, nou = TipusDAssignatura.objects.get_or_create(tipus_assignatura='Unitat Formativa')
    if nou:
        tipus.ambit_on_prendre_alumnes='N'
        tipus.capcelera='Mòdul professional'
    tipus.save()
    
    #
    # Professorat
    #
    parametre_passwd, _ = ParametreKronowin.objects.get_or_create(nom_parametre='passwd',
                                                            defaults={'valor_parametre': '1234', })
    passwd = parametre_passwd.valor_parametre
    
    if not(('teachers' in dades['document']) and dades['document']['teachers'] and 
           ('teacher' in dades['document']['teachers']) and dades['document']['teachers']['teacher']):
        errors.append('No s''ha definit el professorat')
        return {'errors': errors, 'warnings': warnings, 'infos': infos}

    for p in dades['document']['teachers']['teacher']:
        codiProfessor = p['@id'][3:]
        nom=p.get('surname','')
        profe, nouProfessor = Professor.objects.get_or_create(username=codiProfessor)
        if nouProfessor:
            profe.set_password(passwd)
            profe.last_name=nom
            profe.save()
            profe.groups.add(grupProfessors)
            profe.groups.add(grupProfessionals)
            warnings.append(u'Nou usuari: \'%s\'. Passwd: \'%s\'' % (codiProfessor, passwd))
        
    #
    # Grups
    #
    if not(('classes' in dades['document']) and dades['document']['classes'] and 
           ('class' in dades['document']['classes']) and dades['document']['classes']['class']):
        errors.append('No s''han definit grups')
        return {'errors': errors, 'warnings': warnings, 'infos': infos}

    for gr in dades['document']['classes']['class']:
        nomgrup=gr['@id'][3:]
        tut=gr.get('class_teacher','') # tutor. De moment no es fa servir
        
        galum, n, c, g = esGrupAlumnes(nomgrup,False)
        if (galum):
            grupc, warn=creaGrup(n,c,g,inicurs,ficurs)
            warnings.extend(warn)  
            agrupament=gr.get('longname','')
            if agrupament != '' and agrupament[0] == '*':
                # Sistema alternatiu per assignar agrupaments
                # S'indica amb un * a la descripció del grup dins del xml
                # Ex: '*CL_DAW1A CL_ASX1A'

                llista=agrupament[1:].split()
                warn=creaAgrupaments(grupc, llista, inicurs, ficurs, senseGrups)
                warnings.extend(warn)  
                    
            else:
                if senseGrups:
                    grupc, warn=creaGrup(n,c,'-',inicurs,ficurs)
                    warnings.extend(warn)
                    warn=creaAgrupaments(grupc, ['CL_'+n+c+'-'], inicurs, ficurs, senseGrups)
                    warnings.extend(warn)
                
    _, warn=creaGrup('ALL','1','altres',inicurs,ficurs)
    warnings.extend(warn)  
                    
    #
    #  Aules
    #
    if not(('rooms' in dades['document']) and dades['document']['rooms'] and 
           ('room' in dades['document']['rooms']) and dades['document']['rooms']['room']):
        errors.append('No s''han definit aules')
        return {'errors': errors, 'warnings': warnings, 'infos': infos}
    
    for a in dades['document']['rooms']['room']:
        codiAula=a['@id'][3:]
        descAula=a.get('longname','')
        rAula, nouAula = Aula.objects.get_or_create(nom_aula=codiAula)
        if nouAula:
            rAula.descripcio_aula=descAula
            rAula.save()
            warnings.append(u'Nova aula: \'%s\'' % (codiAula))
            nAulesCreades+=1

    # Si detecto errors plego aquí:
    if errors: return {'errors': errors, 'warnings': warnings, 'infos': infos}

    KronowinToUntis, _ = ParametreKronowin.objects.get_or_create(
        nom_parametre='KronowinToUntis')
    assignatures_amb_professor, _ = ParametreKronowin.objects.get_or_create(
        nom_parametre='assignatures amb professor')

    #
    # lliçons
    #
    if not(('lessons' in dades['document']) and dades['document']['lessons'] and 
           ('lesson' in dades['document']['lessons']) and dades['document']['lessons']['lesson']):
        errors.append('No s''han definit classes')
        return {'errors': errors, 'warnings': warnings, 'infos': infos}

    Horari.objects.update(es_actiu=False)
    
    for l in dades['document']['lessons']['lesson']:
        mat=l.get('lesson_subject','')
        if (mat!=''):
            mat=mat['@id'][3:]
        prof=l.get('lesson_teacher','')
        if (prof!=''):
            prof=prof['@id'][3:]
        # Fusiona grups si n'hi ha varis
        ngrup=l.get('lesson_classes','')
        if (ngrup!=''):
            ngrup=ngrup['@id']
            #  Crear grupo xxxxxNABCD... 
            grup, tipus, warn=fusionaGrups(ngrup, inicurs, ficurs, senseGrups)
            warnings.extend(warn)  
        if 'times' in l and l['times'] and 'time' in l['times'] and l['times']['time']:
            cl=l.get('times').get('time')
            if type(cl)!=list:
                cl = [cl]
            for h in cl:
                dia=h.get('assigned_day','')
                hini=h.get('assigned_starttime','')
                hfi=h.get('assigned_endtime','')
                aula=h.get('assigned_room','')
                if aula!='':
                    aula=aula['@id'][3:]
                canvia, warn, compAssig = creaHorari(mat, prof, grup, tipus, dia, hini, hfi, aula, 
                                                 KronowinToUntis, assignatures_amb_professor)
                warnings.extend(warn)  
                nLiniesLlegides+=1
                nAssignaturesCreades+=compAssig
                if canvia:
                    nHorarisModificats+=1
    
    if (('holidays' in dades['document']) and dades['document']['holidays'] and 
        ('holiday' in dades['document']['holidays']) and dades['document']['holidays']['holiday']):
        for l in dades['document']['holidays']['holiday']:
            desc=l.get('longname','')
            iniPer=l.get('starttime',None)
            if iniPer:
                iniPer=datetime.datetime.strptime(iniPer, '%Y%m%d').date()
            fiPer=l.get('endtime',None)
            if fiPer:
                fiPer=datetime.datetime.strptime(fiPer, '%Y%m%d').date()
            
            if iniPer and fiPer:
                diafestiu = Festiu.objects.filter(data_inici_festiu = iniPer,
                                                  data_fi_festiu = fiPer)
                if diafestiu.count()==0:
                    diafestiu=Festiu()
                    diafestiu.data_inici_festiu = iniPer
                    diafestiu.data_fi_festiu = fiPer
                    diafestiu.curs=None
                    diafestiu.franja_horaria_inici=FranjaHoraria.objects.order_by('hora_inici','hora_fi').first()
                    diafestiu.franja_horaria_fi=FranjaHoraria.objects.order_by('hora_inici','hora_fi').last()
                    diafestiu.descripcio=desc
                    diafestiu.save()
                    warnings.append(u'Nou festiu: \'%s\'' % str(diafestiu))

    ambErrors = ' amb errors' if errors else ''
    ambAvisos = ' amb avisos' if not errors and warnings else ''

    infos.append(u'Importació finalitzada' + ambErrors + ambAvisos)
    infos.append(u' ')
    infos.append(u'%d línies llegides' % (nLiniesLlegides,))
    infos.append(u'%d horaris creats o modificats' % (nHorarisModificats))
    infos.append(u'%d aules creades' % (nAulesCreades))
    infos.append(u'%d assignatures Creades' % (nAssignaturesCreades))
    infos.append(u'Recorda reprogramar classes segons el canvia horari')

    # invocar refer 'imparticions'
    from aula.apps.missatgeria.models import Missatge
    missatge = RECORDA_REPROGRAMAR_CLASSES
    tipus_de_missatge = tipusMissatge(missatge)
    msg = Missatge(
        remitent=usuari,
        text_missatge=RECORDA_REPROGRAMAR_CLASSES,
        enllac="/presencia/regeneraImpartir",
        tipus_de_missatge = tipus_de_missatge)
    msg.afegeix_errors(errors)
    msg.afegeix_warnings(warnings)
    msg.afegeix_infos(infos)
    msg.envia_a_usuari(usuari)

    KronowinToUntis, _ = ParametreKronowin.objects.get_or_create(
         nom_parametre='KronowinToUntis')
    KronowinToUntis.valor_parametre='False'
    KronowinToUntis.save()

    return {'errors': errors.sort(), 'warnings': warnings, 'infos': infos}


def creaHorari(mat, prof, grup, tipus, dia, hini, hfi, aula, KronowinToUntis, assignatures_amb_professor):
    
    warnings = []
    compAssig=0

    try:
        horari = Horari()
         
        # franja
        hini=datetime.time(int(hini)//100, int(hini)%100)
        hfi=datetime.time(int(hfi)//100, int(hfi)%100)
        try:
            franja = FranjaHoraria.objects.get(hora_inici = hini, hora_fi = hfi )
        except:
            franja=FranjaHoraria()
            franja.hora_inici=hini
            franja.hora_fi=hfi
            franja.save()

        horari.hora = franja

        
        # grup
        horari.grup=grup;
        
        # professor
        horari.professor = Professor.objects.get(username=prof)

        # ---comprovo si cal afegir el codi professor al codi assignatura:
        cal_afegir_profe = False
        assignatures_amb_professor_value_list = assignatures_amb_professor.valor_parametre.split(',')
        for prefixe_assignatura in [x.strip() for x in assignatures_amb_professor_value_list if bool( x.strip() )]:
            cal_afegir_profe = cal_afegir_profe or mat.startswith(prefixe_assignatura.replace(' ', ''))
            # ---busco l'assignatura:
        mat = (mat + '-' + prof) if cal_afegir_profe else mat

        # matèria
        novamat=False
        if horari.grup is not None:
            try:
                materia = Assignatura.objects.get(curs=horari.grup.curs, codi_assignatura=mat)#,
                                                # tipus_assignatura__ambit_on_prendre_alumnes=tipus)
                materia.nom_assignatura=mat
                materia.tipus_assignatura=TipusDAssignatura.objects.filter(ambit_on_prendre_alumnes=tipus).first()
                materia.save()
            except ObjectDoesNotExist:
                novamat=True
                materia=Assignatura()
                materia.curs=horari.grup.curs
                materia.codi_assignatura=mat
                materia.nom_assignatura=mat
                materia.tipus_assignatura=TipusDAssignatura.objects.filter(ambit_on_prendre_alumnes=tipus).first()
                materia.save()
            except MultipleObjectsReturned:     
                materia = Assignatura.objects.filter(curs=horari.grup.curs, codi_assignatura=mat).order_by('id').last()
                materia.nom_assignatura=mat
                materia.tipus_assignatura=TipusDAssignatura.objects.filter(ambit_on_prendre_alumnes=tipus).first()
                materia.save()
                   
        else:
            try:
                materia = Assignatura.objects.get(curs__isnull=True, codi_assignatura=mat)#,
                                                #tipus_assignatura__ambit_on_prendre_alumnes=tipus)
                materia.nom_assignatura=mat
                materia.tipus_assignatura=TipusDAssignatura.objects.filter(ambit_on_prendre_alumnes=tipus).first()
                materia.save()
            except ObjectDoesNotExist:
                novamat=True
                materia=Assignatura()
                materia.curs=None
                materia.codi_assignatura=mat
                materia.nom_assignatura=mat
                materia.tipus_assignatura=TipusDAssignatura.objects.filter(ambit_on_prendre_alumnes=tipus).first()
                materia.save()       
            except MultipleObjectsReturned:     
                materia = Assignatura.objects.filter(curs__isnull=True, codi_assignatura=mat).order_by('id').last()
                materia.nom_assignatura=mat
                materia.tipus_assignatura=TipusDAssignatura.objects.filter(ambit_on_prendre_alumnes=tipus).first()
                materia.save()
              
        horari.assignatura = materia
        if novamat:
            if horari.grup: curs=horari.grup.curs
            else: curs=None
            warnings.append(u'Nova assignatura: \'%s\' \'%s\'' % (mat, str(curs)))
            compAssig+=1

        
        # aula
        try:
            aula = Aula.objects.get( nom_aula=aula )
        except ObjectDoesNotExist:
            aula=None
        horari.aula = aula
        
        # dia_de_la_setmana
        '''
        n_dia_uk,n_dia_ca,dia_2_lletres,dia_de_la_setmana,es_festiu
        '''
        setmana=[{'n_dia_uk':0,'n_dia_ca':6,'dia_2_lletres':'dg','dia_de_la_setmana':'diumenge','es_festiu':True},
                 {'n_dia_uk':1,'n_dia_ca':0,'dia_2_lletres':'dl','dia_de_la_setmana':'dilluns','es_festiu':False},
                 {'n_dia_uk':2,'n_dia_ca':1,'dia_2_lletres':'dt','dia_de_la_setmana':'dimarts','es_festiu':False},
                 {'n_dia_uk':3,'n_dia_ca':2,'dia_2_lletres':'dc','dia_de_la_setmana':'dimecres','es_festiu':False},
                 {'n_dia_uk':4,'n_dia_ca':3,'dia_2_lletres':'dj','dia_de_la_setmana':'dijous','es_festiu':False},
                 {'n_dia_uk':5,'n_dia_ca':4,'dia_2_lletres':'dv','dia_de_la_setmana':'divendres','es_festiu':False},
                 {'n_dia_uk':6,'n_dia_ca':5,'dia_2_lletres':'ds','dia_de_la_setmana':'dissabte','es_festiu':True},
                 ]

        item=setmana[int(dia)]
        dca=item['n_dia_ca']
        dcurt=item['dia_2_lletres']
        dllarg=item['dia_de_la_setmana']
        dfest=item['es_festiu']
        diaset = DiaDeLaSetmana.objects.filter(n_dia_uk=int(dia))
        if diaset.count()==0:
            horari.dia_de_la_setmana=DiaDeLaSetmana()
            horari.dia_de_la_setmana.n_dia_uk=int(dia)
            horari.dia_de_la_setmana.n_dia_ca=dca
            horari.dia_de_la_setmana.dia_2_lletres=dcurt
            horari.dia_de_la_setmana.dia_de_la_setmana=dllarg
            horari.dia_de_la_setmana.es_festiu=dfest
            horari.dia_de_la_setmana.save()
        else:
            horari.dia_de_la_setmana=DiaDeLaSetmana.objects.get(n_dia_uk=int(dia))

        # horari
        # Si grup i assignatura són iguals no fa falta els dos. Deixem assignatura només.
        nommat=None
        nomgrup=None
        if horari.assignatura is not None:
            nommat=horari.assignatura.nom_assignatura
        if horari.grup is not None:
            nomgrup=horari.grup.descripcio_grup
        if nommat==nomgrup:
            horari.grup = None

        if KronowinToUntis.valor_parametre=='True':
            creaHorari=False
            try:
                nouHorari = Horari.objects.get(
                    hora=horari.hora,
                    professor=horari.professor,
                    assignatura__codi_assignatura=horari.assignatura.codi_assignatura,
                    dia_de_la_setmana=horari.dia_de_la_setmana,
                    es_actiu=False)
            except ObjectDoesNotExist:
                nouHorari = Horari()
                nouHorari.hora=horari.hora
                nouHorari.grup=horari.grup
                nouHorari.professor=horari.professor
                nouHorari.assignatura=horari.assignatura
                nouHorari.dia_de_la_setmana=horari.dia_de_la_setmana
                creaHorari=True
            except MultipleObjectsReturned:
                nouHorari = Horari.objects.filter(
                    hora=horari.hora,
                    professor=horari.professor,
                    assignatura__codi_assignatura=horari.assignatura.codi_assignatura,
                    dia_de_la_setmana=horari.dia_de_la_setmana,
                    es_actiu=False,
                    impartir__isnull = False)
                if nouHorari.count()>0:
                    nouHorari= nouHorari.order_by('id').first()
                else:
                    nouHorari = Horari.objects.filter(
                        hora=horari.hora,
                        professor=horari.professor,
                        assignatura__codi_assignatura=horari.assignatura.codi_assignatura,
                        dia_de_la_setmana=horari.dia_de_la_setmana,
                        es_actiu=False).order_by('id').first()
                   
            aulaAntiga=nouHorari.aula
            if not creaHorari and aulaAntiga==horari.aula:
                # sense canvis
                resultat=False
            else:
                # nou horari o canvi d'aula
                resultat=True
                
            nouHorari.assignatura=horari.assignatura
            nouHorari.grup=horari.grup
            nouHorari.aula = horari.aula
            nouHorari.es_actiu=True
            nouHorari.save()
        else:
            creaHorari=False
            try:
                nouHorari = Horari.objects.get(
                    hora=horari.hora,
                    grup=horari.grup,
                    professor=horari.professor,
                    assignatura=horari.assignatura,
                    dia_de_la_setmana=horari.dia_de_la_setmana,
                    es_actiu=False)
            except ObjectDoesNotExist:
                nouHorari = Horari()
                nouHorari.hora=horari.hora
                nouHorari.grup=horari.grup
                nouHorari.professor=horari.professor
                nouHorari.assignatura=horari.assignatura
                nouHorari.dia_de_la_setmana=horari.dia_de_la_setmana
                creaHorari=True
            except MultipleObjectsReturned:
                nouHorari = Horari.objects.filter(
                    hora=horari.hora,
                    grup=horari.grup,
                    professor=horari.professor,
                    assignatura=horari.assignatura,
                    dia_de_la_setmana=horari.dia_de_la_setmana,
                    es_actiu=False).order_by('id').first()
                   
            aulaAntiga=nouHorari.aula
            if not creaHorari and aulaAntiga==horari.aula:
                # sense canvis
                resultat=False
            else:
                # nou horari o canvi d'aula
                resultat=True
                
            nouHorari.aula = horari.aula
            nouHorari.es_actiu=True
            nouHorari.save()
        
        return resultat,warnings,compAssig
        
    except Exception as e:
        warnings.append('Horari no importat, [' + str(e) + '] :' + mat + ',' + prof + ',' + str(grup) + ',' + dia + ',' + 
                        str(hini) + ',' + str(hfi) + ',' + str(aula))
        warnings.append( traceback.format_exc() )
        return False, warnings,compAssig
