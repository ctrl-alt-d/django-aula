# This Python file uses the following encoding: utf-8

from datetime import date
from aula.apps.relacioFamilies.models import Responsable
from django.forms.models import model_to_dict

def creaResponsables(alumne, responsables):
    '''
    alumne és l'alumne dels responsables.
    responsables és una llista de diccionaris, cada diccionari conté els camps d'un responsable.
    Crea els responsables de la llista o els actualitza, i els associa a l'alumne.
    '''
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
        else:
            resp=resp[0]
            actual=model_to_dict(resp)
            camps=dades.keys()
            # Actualitza amb les noves dades
            for f in camps:
                actual[f]=dades[f]
            if 'user_associat' in actual: del actual['user_associat']
            if 'alumnes_associats' in actual: del actual['alumnes_associats']
            if 'alumne_actual' in actual: del actual['alumne_actual']
            respMod=Responsable(**actual)
            respMod.user_associat=resp.user_associat
            respMod.alumnes_associats.set(resp.alumnes_associats.all())
            respMod.alumne_actual=resp.alumne_actual
            if respMod.data_baixa:
                # Si era baixa -> ara és alta
                respMod.data_baixa = None
                respMod.motiu_bloqueig = ''
            respMod.save()
            respMod.alumnes_associats.add(alumne)


