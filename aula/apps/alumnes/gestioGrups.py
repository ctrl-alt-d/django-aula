from django.apps import apps
from django.db.models import F
from aula.apps.alumnes.models import Grup
from aula.apps.extUntis.models import Agrupament

def grupsPromocionar():
    '''Determina els grups que són susceptibles de promoció
    
    Els grups de desdoblaments no han d'apareixer a la llista de grups a Promocionar
    Retorna queryset dels grups
    '''
    
    idsgrupsDesdoblaments=list(set(Agrupament.objects.annotate(grupValue=F('grup_horari__id')).values('grupValue'))-\
                        set(Agrupament.objects.annotate(grupValue=F('grup_alumnes__id')).values('grupValue')))
    return Grup.objects.exclude(id__in = idsgrupsDesdoblaments).order_by('descripcio_grup')

def llistaIdsAgrupament(grupid):
    '''Determina tots els grups que aporten alumnes a grupid, segons els agrupaments
    
    grupid id del grup que volem saber d'on treu els alumnes
    Retorna una llista que conté tots els id de grup que aporten alumnes al grup indicat

    '''
    
    llista=set()
    q_Agrup=Agrupament.objects.filter(grup_horari=grupid).values('grup_alumnes').distinct()
    if not(q_Agrup.exists()):
        # No hi ha agrupament
        return { grupid }
    if q_Agrup.count()==1 and q_Agrup.first()['grup_alumnes']==grupid:
        # Agrupament és el mateix grup
        return { grupid }
    # Agrupaments dels altres grups
    for g in q_Agrup:
        if (g['grup_alumnes']==grupid):
            # Si és el mateix grup, s'afegeix sense fer més recerca
            llista.add(grupid)
        else:
            # Es continua la recerca
            llista.update(llistaIdsAgrupament(g['grup_alumnes']))
    return llista

def grupsAgrupament(grup):
    '''Retorna queryset dels grups que aporten alumnes a grup.

    grup del que volem saber d'on treu els alumnes
    Retorna queryset dels grups trobats
    
    '''
    
    q_Agrup=llistaIdsAgrupament(grup.id)
    return Grup.objects.filter(id__in = q_Agrup).filter(alumne__isnull = False).distinct()

#  amorilla@xtec.cat
#  He canviat la ubicació d'aquesta funció.
#  Amb els canvis realitzats donava error en el migrate (referència circular)
def grupsPotencials(horari):
    grups_potencials = None
    codi_ambit = horari.assignatura.tipus_assignatura.ambit_on_prendre_alumnes if horari.assignatura.tipus_assignatura is not None else 'G'
    Grup = apps.get_model( 'alumnes','Grup')
    if codi_ambit == 'I':
        grups_potencials= Grup.objects.filter(alumne__isnull = False).distinct()
    elif codi_ambit == 'N':
        grups_potencials= Grup.objects.filter(alumne__isnull = False).filter( curs__nivell = horari.grup.curs.nivell ).distinct()
    elif codi_ambit == 'C':
        grups_potencials= Grup.objects.filter(alumne__isnull = False).filter( curs = horari.grup.curs ).distinct()
        # Nous àmbits on escollir alumnes
        # 'A'  Agrupament. Llista de grups concreta
        # 'AN' Agrupament amb nivell. Tots els grups dels mateixos nivells.
    elif codi_ambit[0] == 'A':
        q_grups=grupsAgrupament(horari.grup)
        if codi_ambit=='AN':
            llista=q_grups.values('curs__nivell')
            q_grups=Grup.objects.filter( curs__nivell__in = llista).filter(alumne__isnull = False).distinct()
        grups_potencials= q_grups
    elif codi_ambit == 'G':
        if horari.grup:
            grups_potencials=Grup.objects.filter( pk = horari.grup.pk  )
        else:
            grups_potencials=Grup.objects.none()
    return grups_potencials.order_by('descripcio_grup')
