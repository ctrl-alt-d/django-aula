from django.apps import apps
from django.db.models import F
from aula.apps.alumnes.models import Grup
from aula.apps.extUntis.models import Agrupament

def grupsPromocionar():
    '''Determina els grups que són susceptibles de promoció
    
    Els grups de desdoblaments no han d'apareixer a la llista de grups a Promocionar
    Retorna queryset dels grups
    '''
    
    idsgrupsDesdoblaments=Agrupament.objects.annotate(grupValue=F('grup_horari__id')).values('grupValue').difference( \
                        Agrupament.objects.annotate(grupValue=F('grup_alumnes__id')).values('grupValue'))
    return Grup.objects.exclude(id__in = idsgrupsDesdoblaments).order_by('descripcio_grup')

def grupsAgrupament(grup):
    '''Determina tots els agrupaments d'un grup
    
    grup del que volem els seus agrupaments
    Retorna un queryset que conté tots els grups que aporten alumnes al grup indicat

    '''
    
    q_Agrup=Agrupament.objects.filter(grup_horari=grup).values('grup_alumnes').distinct()
    if not(q_Agrup.exists()):
        # No hi ha agrupament
        return Grup.objects.filter(pk = grup.pk).filter(alumne__isnull = False).distinct()
    if q_Agrup.count()==1 and q_Agrup.first()['grup_alumnes']==grup.id:
        # Agrupament és el mateix grup
        return Grup.objects.filter(pk = grup.pk).filter(alumne__isnull = False).distinct()
    # Agrupament de dos o més elements
    query=Grup.objects.none()
    for g in q_Agrup:
        ng=Grup.objects.filter(pk = g['grup_alumnes']).filter(alumne__isnull = False).distinct()
        if not ng:
            continue
        if (ng.first()==grup):
            # Si és el mateix grup, s'afegeix sense fer més recerca
            query=query.union(ng)
        else:
            # Es continua la recerca
            query=query.union(grupsAgrupament(ng.first()))
    return query

#  amorilla@xtec.cat
#  He canviat la ubicació d'aquesta funció.
#  Amb els canvis realitzats donava error en el migrate (referència circular)
def grupsPotencials(horari):
    grups_potencials = None
    codi_ambit = horari.assignatura.tipus_assignatura.ambit_on_prendre_alumnes if horari.assignatura.tipus_assignatura is not None else 'G'
    Grup = apps.get_model( 'alumnes','Grup')
    if codi_ambit == 'I':
        grups_potencials= Grup.objects.filter(alumne__isnull = False)
    elif codi_ambit == 'N':
        grups_potencials= Grup.objects.filter(alumne__isnull = False).filter( curs__nivell = horari.grup.curs.nivell  )
    elif codi_ambit == 'C':
        grups_potencials= Grup.objects.filter(alumne__isnull = False).filter( curs = horari.grup.curs  )
        # Nous àmbits on escollir alumnes
        # 'A'  Agrupament. Llista de grups concreta
        # 'AN' Agrupament amb nivell. La llista i altres grups dels mateixos nivells.
    elif codi_ambit[0] == 'A':
        q_grups=grupsAgrupament(horari.grup)
        if codi_ambit=='AN':
            llista=q_grups.values('curs__nivell__nom_nivell')
            valors=[]
            for i in llista: valors.append(i.get('curs__nivell__nom_nivell'))
            q_grups=Grup.objects.filter( curs__nivell__nom_nivell__in = valors)
        grups_potencials= q_grups.filter(alumne__isnull = False).distinct()
    elif codi_ambit == 'G':
        if horari.grup:
            grups_potencials=Grup.objects.filter( pk = horari.grup.pk  )
        else:
            grups_potencials=Grup.objects.none()
    return grups_potencials.distinct().order_by('descripcio_grup')
