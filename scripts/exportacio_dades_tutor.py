import json
from aula.apps.tutoria.models import SeguimentTutorial
seguiments = []
for s in SeguimentTutorial.objects.all():
    d={}
    d['nom']=s.nom
    d['cognoms']=s.cognoms
    d['seguiments'] = []
    for r in s.seguimenttutorialrespostes_set.all():
        dr={}
        dr['any_curs_academic'] = r.any_curs_academic
        dr['pregunta'] = r.pregunta
        dr['resposta'] = r.resposta
        d['seguiments'].append( dr )
    d['actuacions_tutor']=[]
    for a in s.alumne.actuacio_set.filter( qui_fa_actuacio = 'T' ):
        da={}
        da['professional'] = str( a.professional )
        da['moment_actuacio'] = a.moment_actuacio.strftime("%d/%m/%y")
        da['amb_qui_es_actuacio'] = a.get_amb_qui_es_actuacio_display()
        da['assumpte'] = a.assumpte
        da['actuacio'] = a.actuacio
        d['actuacions_tutor'].append( da )
    seguiments.append( d ) 

f= open('/opt/django/exportacio_tutors/dades.json', 'w')
json.dump(seguiments, f )
f.close()


