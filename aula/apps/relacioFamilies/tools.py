# This Python file uses the following encoding: utf-8

from datetime import date
from aula.apps.relacioFamilies.models import Responsable
from django.forms.models import model_to_dict

def creaResponsables(alumne, responsables, manteDades=False):
    '''
    alumne és l'alumne dels responsables.
    responsables és una llista de diccionaris, cada diccionari conté els camps d'un responsable.
    manteDades si True no modifica les dades actuals, del responsable existent, amb les del diccionari.
    Crea els responsables de la llista o els actualitza, i els associa a l'alumne.
    Treu l'associació dels responsables que ja no corresponen.
    '''
    dnis_resp=[]
    nous=0
    for dades in responsables:
        if "dni" not in dades or not bool(dades["dni"]): continue
        resp=Responsable.objects.filter(dni=dades["dni"])
        if not resp.exists():
            # Responsable nou
            resp=Responsable(**dades)
            resp.data_alta = date.today()
            resp.motiu_bloqueig = u'No sol·licitat'
            resp.save()
            resp.alumnes_associats.add(alumne)
            nous += 1
        else:
            resp=resp[0]
            actual=model_to_dict(resp,exclude=['user_associat', 'alumnes_associats'])
            if not manteDades:
                camps=dades.keys()
                # Actualitza amb les noves dades
                for f in camps:
                    actual[f]=dades[f]
            respMod=Responsable(**actual)
            respMod.user_associat=resp.user_associat
            if respMod.data_baixa:
                # Si era baixa -> ara és alta
                respMod.data_baixa = None
                respMod.motiu_bloqueig = ''
                respMod.user_associat.is_active=True
                respMod.user_associat.save()
            else:
                respMod.alumnes_associats.set(resp.alumnes_associats.all())
            respMod.save()
            respMod.alumnes_associats.add(alumne)
        dnis_resp.append(resp.dni)
    alumne.esborraAntics_responsables(dnis_resp)
    alumne.save()
    return nous

