# This Python file uses the following encoding: utf-8
from aula.apps.sortides.models import Sortida, NotificaSortida

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
            
                    
                    
