from django.apps import apps
from aula.apps.extUntis.sincronitzaUntis import grupsAmbAlumnes, grupsAgrupament

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
