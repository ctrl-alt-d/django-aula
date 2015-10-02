### per data, centre, tutors, ... ###

select string_agg(id::text, ', ' order by id), max( a.nom || ' ' || a.cognoms)  , min( a.nom || ' ' || a.cognoms)  
    from alumnes_alumne a 
group by a.data_neixement, a.centre_de_procedencia , a.tutors, a.adreca
  having count(*) > 1;

#### per nom ####

#cal instal·lar el mòdul de postgres per treballar sense accents:
apt-get install postgresql-contrib-9.1
CREATE EXTENSION unaccent;
  
#Aquí agrupant sense accents, ull en pot trobar que tinguin el mateix nom realment al centre:  
select string_agg(id::text, ', ' order by id), unaccent(a.nom), unaccent(a.cognoms)
    from alumnes_alumne a 
group by unaccent(a.nom), unaccent(a.cognoms)
  having count(*) > 1;

#Aquí agrupant tenint en compte els accents:  
select string_agg(id::text, ', ' order by id), unaccent(a.nom), unaccent(a.cognoms)
    from alumnes_alumne a 
group by a.nom, a.cognoms
  having count(*) > 1;  
  
#aquí preparant la sortida per agrupar-los:
select 'f(' || string_agg(id::text, ', ' order by id) || ')'  
    from alumnes_alumne a 
group by unaccent(a.nom), unaccent(a.cognoms)
  having count(*) > 1;
  
#agrupant alumnes:
from aula.apps.alumnes.tools import fusiona_alumnes as ff
from aula.apps.alumnes.models import Alumne as A
def f(a,b):
    aa=A.objects.get(id=a)
    bb=A.objects.get(id=b)
    ff(aa,[bb])

f(1,2)
    