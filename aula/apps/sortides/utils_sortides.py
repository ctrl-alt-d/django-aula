# This Python file uses the following encoding: utf-8
from aula.apps.sortides.models import Sortida, NotificaSortida
from aula.settings import CUSTOM_CODI_COMERÇ, CUSTOM_KEY_COMERÇ, CUSTOM_REDSYS_ENTORN_REAL

def TPVsettings(user):
    '''
    Determina els paràmetres del TPV
    Si l'usuari pertany a 'tpvs', fa servir el TPV que coincideix amb el seu username
    En altre cas fa servir el TPV principal 'centre'.
    Si no pot seleccionar cap TPV, fa servir els settings a settings_local.py o settings.py
    Retorna codi comerç, key, entorn real
    '''
    from django.contrib.auth.models import Group
    from aula.apps.sortides.models import TPV

    tp=Group.objects.get_or_create(name= 'tpvs' )
    tpv=None
    if tp and tp[0] in user.groups.all():
        tpv = TPV.objects.filter(nom=user.username)
    else:
        tpv = TPV.objects.filter(nom='centre')
    if tpv:
        return tpv[0].codi, tpv[0].key, tpv[0].entornReal
    else:
        return CUSTOM_CODI_COMERÇ, CUSTOM_KEY_COMERÇ, CUSTOM_REDSYS_ENTORN_REAL

def notifica_sortides():
    """
    Per a totes les activitats / sortides en estat R ó G ( Revisades o Gestionades per Cap d'Estudis )
    faig el següent:
    - Si l'activitat no té alumnes: esborro les 'notificacions'
    - Si l'activitat té alumnes: sincronitzo
    """
    
    activitats = list( Sortida.objects.filter( estat__in = ['R', 'G', ] ) )
    for activitat in activitats:
        alumnes = list( activitat.alumnes_convocats.all() )
        alumnes_notificats = [ n.alumne for n in activitat.notificasortida_set.all() ]
        #afegeixo les notificacions que poden faltar:
        for alumne in alumnes:
            if alumne not in alumnes_notificats:
                NotificaSortida.objects.create(
                                                alumne = alumne,
                                                sortida = activitat,                            
                                               )
            else:
                alumnes_notificats.remove(alumne)
        #esborro notificacions d'alumnes que ja no venen:
        activitat.notificasortida_set.filter( alumne__in = alumnes_notificats ).delete()
            
                    
                    
