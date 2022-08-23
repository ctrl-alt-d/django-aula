# This Python file uses the following encoding: utf-8

from aula.apps.extPreinscripcio.models import Preinscripcio, Nivell2Aula
from aula.apps.missatgeria.missatges_a_usuaris import tipusMissatge, IMPORTACIO_PREINSCRIPCIO_FINALITZADA
from aula.apps.missatgeria.models import Missatge
from django.contrib.auth.models import Group
from django.conf import settings
import numbers

def neteja(value):
    if value and isinstance(value, str) and value.startswith('="'):
        lon=len(value)
        value=value[2:lon-1] # '="......"' -->  '......'
    return value

def assignaDades(preinscripcio, index, value, col_indexs):
    '''
    Afegeix al diccionari preinscripcio el {camp:valor}, segons col_indexs[index] i value 
    '''
    
    if index in col_indexs and value:
        value=neteja(value)
        field=col_indexs[index]
        #Si té opcions extra es gestionen
        if isinstance(field, dict):
            # Convertir a minúscules o majúscules
            if 'case' in field and field['case']:
                value=str(value).lower() if field['case']=='L' else str(value).upper()
            if 'append' in field and field['append']:
                #Afegir al valor existent separant amb un espai
                if field['field'] not in preinscripcio:
                    preinscripcio[field['field']]=value
                else:
                    preinscripcio[field['field']]=str(preinscripcio[field['field']])+" "+str(value)
            else:
                #Assigna directament
                if 'field' in field and field['field']:
                    preinscripcio[field['field']]=value
        else:
            # field, identificador a la base de dades
            preinscripcio[field]=value
    return preinscripcio

def creadict(row, colnames):
    '''
    Crea diccionari amb les parelles {n:camp} segons la fila row i camps de colnames
    '''
    return {n: colnames[str(cell).lower()] for n, cell in enumerate(row)
                   if str(cell).lower() in colnames}

def getCampPn(cap, num, capçaleres, data):
    label=cap+" p"+str(num)
    capcentre= [nc for nc, cellc in enumerate(capçaleres) if label==cellc.lower()]
    if capcentre:
        return neteja(data[capcentre[0]])
    capcentre= [nc for nc, cellc in enumerate(capçaleres) if cap==cellc.lower()]
    if capcentre:
        return neteja(data[capcentre[0]])
    return None

def acceptat(row, capçaleres, preinscripcio, codi):
    for n, cell in enumerate(row):
        if cell=="Assignada":
            cap=capçaleres[n].lower()
            pos=cap.rfind("p")
            if pos!=-1:
                num=int(cap[pos+1:])
                if getCampPn("codi centre", num, capçaleres, row)==codi:
                    preinscripcio.update({'codiestudis':getCampPn("codi ensenyament", num, capçaleres, row)})
                    preinscripcio.update({'nomestudis':getCampPn("nom ensenyament", num, capçaleres, row)})
                    preinscripcio.update({'codimodalitat':getCampPn("codi modalitat", num, capçaleres, row)})
                    preinscripcio.update({'nommodalitat':getCampPn("modalitat", num, capçaleres, row)})
                    preinscripcio.update({'curs':getCampPn("curs", num, capçaleres, row)})
                    preinscripcio.update({'regim':getCampPn("règim", num, capçaleres, row)})
                    preinscripcio.update({'torn':getCampPn("torn", num, capçaleres, row)})
                    preinscripcio.update({'estat':'Assignada'})
                    return True
    return False

def convertirCodiEstudis(codiestudis):
    from aula.apps.alumnes.models import Nivell
    n=Nivell.objects.filter(nom_nivell=codiestudis)
    if codiestudis and not n:
        np=Nivell2Aula.objects.filter(nivellgedac=codiestudis)
        if not np:
            np=Nivell2Aula(nivellgedac=codiestudis)
            np.save()
        else:
            if np[0].nivellDjau:
                return np[0].nivellDjau.nom_nivell
    return codiestudis

def actualitzaPreinscripcio():
    llp=Preinscripcio.objects.all()
    for p in llp:
        codiestudis=convertirCodiEstudis(p.codiestudis)
        if codiestudis!=p.codiestudis:
            p.codiestudis=codiestudis
            p.save(update_fields=["codiestudis"])

def obrefull(f):
    import csv
    from io import StringIO
    
    #el GEDAC proporciona els fitxers csv en format iso-8859-15 i final d'estil MacOS
    text = f.read().decode("iso-8859-1")
    textok = text.replace('\r', '\n')
    fcsv=StringIO(textok)
    rows=list(csv.reader(fcsv, delimiter=';', dialect=csv.excel))
    f.close()
    return rows
                
def creaPreins(row, col_indexs):
    preinscripcio={}
    for index, cell in enumerate(row):
        if bool(cell):
            if isinstance(cell, str):
                cell=cell.strip()
            else:
                if isinstance(cell, numbers.Number):
                    cell=str(cell)
        preinscripcio=assignaDades(preinscripcio, index, cell, col_indexs)
    return preinscripcio

def sincronitza(f, user = None):
    from django.utils.datetime_safe import datetime
    
    errors = []
    warnings= []
    infos= []
    
    try:
        # Carregar full de càlcul
        rows = obrefull(f)
        if not rows:
            errors.append('Fitxer incorrecte')
            return {'errors': errors, 'warnings': [], 'infos': []}
    except:
        errors.append('Fitxer incorrecte')
        return {'errors': errors, 'warnings': [], 'infos': []}
    
    if not settings.CODI_CENTRE:
        errors.append("No s\'ha definit el codi de centre a settings")
        return {'errors': errors, 'warnings': [], 'infos': []}
    
    info_nAlumnesLlegits=0

    # columnes que s'importaran,  camp excel : camp base de dades 
    colnames = {
        'convocatòria':'any',
        'nom': 'nom',
        'primer cognom': 'cognoms',
        'segon cognom': {'field': 'cognoms', 'append' : True},
        'identificació ralc': 'ralc',
        'ident. ralc': 'ralc',
        'codi ensenyament': 'codiestudis',
        'nom ensenyament': 'nomestudis',
        'codi modalitat': 'codimodalitat',
        'modalitat': 'nommodalitat',
        'curs': 'curs',
        'règim': 'regim',
        'torn': 'torn',
        'dni': {'field': 'identificador', 'case' : 'U'},
        'nie': {'field': 'identificador', 'case' : 'U'},
        'pass': {'field': 'identificador', 'case' : 'U'},
        'tis': 'tis',
        'data naixement': 'naixement',
        'sexe': 'sexe',
        'nacionalitat': 'nacionalitat',
        'país naixement': 'paisnaixement',
        'tipus via': 'adreça',
        'nom via': {'field': 'adreça', 'append' : True},
        'número via': {'field': 'adreça', 'append' : True},
        'altres dades': {'field': 'adreça', 'append' : True},
        'província residència': 'provincia',
        'municipi residència': 'municipi',
        'localitat residència': 'localitat',
        'cp': 'cp',
        'país residència': 'paisresidencia',
        'telèfon': 'telefon',
        'correu electrònic': {'field': 'correu', 'case' : 'L'},
        'tipus doc. tutor 1': 'tdoctut1',
        'núm. doc. tutor 1': 'doctut1',
        'nom tutor 1': 'nomtut1',
        'primer cognom tutor 1': 'cognomstut1',
        'segon cognom tutor 1': {'field': 'cognomstut1', 'append' : True},
        'tipus doc. tutor 2': 'tdoctut2',
        'núm. doc. tutor 2': 'doctut2',
        'nom tutor 2': 'nomtut2',
        'primer cognom tutor 2': 'cognomstut2',
        'segon cognom tutor 2': {'field': 'cognomstut2', 'append' : True},
        'codi centre proc.': 'codicentreprocedencia',
        'nom centre proc.': 'centreprocedencia',
        'codi ensenyament proc.': 'codiestudisprocedencia',
        'nom ensenyament proc.': 'estudisprocedencia',
        'curs proc.': 'cursestudisprocedencia',
        'centre assignat':'centreassignat',
        'estat sol·licitud': 'estat',
        }
    
    #Crea diccionari núm.col.:nom col. segons la fila 0 i colnames
    col_indexs = creadict(rows[0], colnames)
    
    if 'centreassignat' in col_indexs.values():
        peticions=False
    else:
        peticions=True
    
    totsCodiEstudis=set()
    for row in rows[1:]:
       
        preinscripcio=creaPreins(row, col_indexs)
        
        if 'naixement' in preinscripcio:
            preinscripcio['naixement'] = datetime.strptime(preinscripcio['naixement'], '%d/%m/%Y')
        #if 'cp' in preinscripcio and preinscripcio['cp'].startswith("="): 
        #    preinscripcio['cp']=preinscripcio['cp'][2:7] # '="NNNNN"'
        if 'any' in preinscripcio and not isinstance(preinscripcio['any'],int):
            try:
                nany=int(preinscripcio['any'][-9:-5])  # 'XXXXXXXXXXXX 20xx/20yy'
            except Exception as e:
                nany=datetime.today().year
            preinscripcio['any']=nany
        #if 'centreassignat' in preinscripcio and preinscripcio['centreassignat'].startswith("="): 
        #    preinscripcio['centreassignat']=preinscripcio['centreassignat'][2:10]  # '="NNNNNNNN"'
        if 'adreça' in preinscripcio:
            components=preinscripcio['adreça'].split()
            nova=''
            i=0
            while i<len(components):
                c=components[i]
                i+=1
                if c.endswith(":") and len(c)>1:
                    lletra=c[0]
                    if i<len(components): dada=components[i]
                    else: dada='--'
                    i+=1
                    if dada!="--":
                        nova=nova+' '+lletra+':'+dada
                else:
                    if c!='Altres':
                        nova=nova+' '+c
            preinscripcio['adreça']=nova[1:]

        if (peticions and acceptat(row, rows[0], preinscripcio, settings.CODI_CENTRE)) or \
            (not peticions and preinscripcio.get('estat','')=='Validada' and \
            preinscripcio.get('centreassignat','')==settings.CODI_CENTRE):
            try:
                p=Preinscripcio(**preinscripcio)
                query=Preinscripcio.objects.filter(ralc=p.ralc, any=p.any)
                if query:
                    p=query[0]
                    estat=preinscripcio.pop('estat','')
                    if estat=='Assignada': preinscripcio.update({'estat':estat})
                    else:
                        if p.estat.startswith('Marca'):
                            preinscripcio.update({'estat': p.estat[5:]})
                    for field, value in iter(preinscripcio.items()):
                        setattr(p, field, value)
                p.estat='Marca'+p.estat
                p.codiestudis=convertirCodiEstudis(p.codiestudis)
                #guarda el conjunt de tots els codiestudis
                totsCodiEstudis.add(p.codiestudis)
                p.save()
                info_nAlumnesLlegits += 1
            except Exception as e:
                errors.append(str(e)+": "+str(preinscripcio))
                
    # Delete preinscripcions sense matrícula dels mateixos estudis, què no apareixen ara al fitxer
    llp=Preinscripcio.objects.filter(estat__startswith='Marca')
    if llp:
        nany=llp[0].any
    else:
        nany=datetime.today().year
    Preinscripcio.objects.filter(any=nany, matricula__isnull=True, estat__in=['Validada','Assignada',], codiestudis__in=totsCodiEstudis).delete()
    # Elimina 'Marca especial' de la resta
    Preinscripcio.objects.filter(estat='MarcaValidada').update(estat='Validada')
    Preinscripcio.objects.filter(estat='MarcaAssignada').update(estat='Assignada')
    
    infos.append(u'{0} alumnes llegits'.format(info_nAlumnesLlegits) )

    missatge = IMPORTACIO_PREINSCRIPCIO_FINALITZADA
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
