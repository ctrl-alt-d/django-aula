from django import template
from aula.apps.extPreinscripcio.models import Preinscripcio
from aula.apps.sortides.models import QuotaPagament
from aula.apps.matricula.models import Document
from django.conf import settings

register = template.Library()

@register.filter(name='torn')
def getTorn(matricula):
    '''
    Retorna el torn de la preinscripció, si existeix.
    'matí' 'tarda' o ''
    '''
    if matricula and matricula.alumne:
        p=Preinscripcio.objects.filter(ralc=matricula.alumne.ralc, any=matricula.any, 
                                       codiestudis=matricula.curs.nivell.nom_nivell, curs=matricula.curs.nom_curs)
        if p:
            return p[0].torn
    return ''

def nomes1Fracc(pagtax):
    '''
    Comprova pagaments de les taxes
    Retorna True si té fraccionament de taxes i només ha pagat la 1a fracció.
            False en altre cas.
    TODO  hauria de acceptar qualsevol quantitat de fraccionament >2
    '''

    if pagtax and pagtax.count()==2:
        return ((pagtax[0].pagament_realitzat and not pagtax[1].pagament_realitzat) \
                or (not pagtax[0].pagament_realitzat and pagtax[1].pagament_realitzat))
    else:
        return False

@register.simple_tag(name='ctrlPag')
def ctrlPag(matricula):
    missatge=None
    color=''
    quotamat=settings.CUSTOM_TIPUS_QUOTA_MATRICULA
    if matricula.getPagament:
        if matricula.pagamentFet:
            missatge=quotamat+" pagat"
            color=''
        else:
            missatge=quotamat+" pendent"
            color='Tomato'
    else:
        missatge="no té quota "+quotamat
        color='DarkMagenta'
    return {'mess':missatge,'color':color}

@register.simple_tag(name='ctrlTax')
def ctrlTax(matricula):
    missatge=None
    color=''
    taxes=matricula.curs.nivell.taxes
    if taxes:
        pagtax=QuotaPagament.objects.filter(alumne=matricula.alumne, quota__any=matricula.any,
                                 quota__tipus=taxes)
        if pagtax:
            if pagtax.filter(pagament_realitzat=False):
                if nomes1Fracc(pagtax):
                    missatge=taxes.nom+" 1a fracció"
                    color=''
                else:
                    missatge=taxes.nom+" pendent"
                    color='Tomato'
            else:
                missatge=taxes.nom+" pagat"
                color=''
        else:
            missatge="no té "+taxes.nom
            color='DarkMagenta'
    return {'mess':missatge,'color':color}

@register.filter(name='documents')
def getDocuments(matricula):
    '''
    Documents de la matrícula
    '''
    return Document.objects.filter(matricula=matricula).order_by('pk')
