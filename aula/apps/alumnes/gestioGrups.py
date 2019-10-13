from django.apps import apps
from django.db.models import Q
from aula.apps.alumnes.models import Grup, Alumne
from aula.apps.extUntis.models import Agrupament

def grupsAmbAlumnes(q_llista):
    '''retorna grups amb alumnes d'un queryset.
    
    q_llista queryset de grups que volem verificar
    Retorna un altre queryset amb només els grups que tenen alumnes
    
    '''
    
    grups=set()
    for g in q_llista:
        if Alumne.objects.filter(grup = g).count()>0:
            grups.add(g.id)
    return Grup.objects.filter(id__in = grups).distinct()

def grupsAmbMatricula(q_llista):
    '''retorna grups de saga o esfera d'un queryset.
    
    q_llista queryset de grups que volem verificar
    Retorna un altre queryset amb només els grups que tenen alumnes matriculats de saga o esfera
    
    '''
    
    return q_llista.filter(Q(grup2aulasaga_set__isnull = False) | Q(grup2aulaesfera_set__isnull = False)).distinct()

def grupsAgrupament(grup):
    '''Determina tots els agrupaments d'un grup
    
    grup del que volem els seus agrupaments
    Retorna una llista que conté tots els id de grup que aporten alumnes al grup indicat
    
    '''
    llista=set()
    q_Agrup=Agrupament.objects.filter(grup_horari=grup).values('grup_alumnes')
    if q_Agrup.count()==0:
        llista.add(grup.id)
        return llista
    if q_Agrup.count()==1 and q_Agrup.first()['grup_alumnes']==grup.id:
        llista.add(grup.id)
        return llista
    for g in q_Agrup:
        ng=Grup.objects.get(pk = g['grup_alumnes'])
        if (ng==grup): continue
        llista.update(grupsAgrupament(ng))
    return llista

#
#  He canviat la ubicació d'aquesta funció.
#  Amb els canvis realitzats donava error en el migrate (referència circular)
def grupsPotencials(horari):
    grups_potencials = None
    codi_ambit = horari.assignatura.tipus_assignatura.ambit_on_prendre_alumnes if horari.assignatura.tipus_assignatura is not None else 'G'
    Grup = apps.get_model( 'alumnes','Grup')
    if codi_ambit == 'I':
        grups_potencials= grupsAmbAlumnes(Grup.objects.all())
    elif codi_ambit == 'N':
        grups_potencials= grupsAmbAlumnes(Grup.objects.filter( curs__nivell = horari.grup.curs.nivell  ))
    elif codi_ambit == 'C':
        grups_potencials= grupsAmbAlumnes(Grup.objects.filter( curs = horari.grup.curs  ))
        # Nous àmbits on escollir alumnes
        # 'A'  Agrupament. Llista de grups concreta
        # 'AN' Agrupament amb nivell. La llista i altres grups dels mateixos nivells.
    elif codi_ambit[0] == 'A':
        q_Agrup=grupsAgrupament(horari.grup)
        q_grups=Grup.objects.filter(id__in = q_Agrup).distinct()
        if codi_ambit=='AN':
            q_grups1=Grup.objects.filter( curs__nivell__nom_nivell__in = q_grups.values('curs__nivell__nom_nivell')).distinct()
            q_grups=q_grups.union(q_grups1)
        grups_potencials= grupsAmbAlumnes(q_grups)
    elif codi_ambit == 'G':
        if horari.grup:
            grups_potencials=Grup.objects.filter( pk = horari.grup.pk  )
        else:
            grups_potencials=Grup.objects.none()
    return grups_potencials.order_by('descripcio_grup')
