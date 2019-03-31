###  SLUGIFYING ###

from django.contrib.auth.models import User as U
d=U.objects.get(username='coor')
c=(d,True)

from django.template.defaultfilters import slugify
from aula.apps.alumnes.models import Alumne as A
from aula.apps.alumnes.tools import fusiona_alumnes as f

a = list(A.objects.all() )

criteri_nom_i_data = lambda x: u"{0}{1}".format( x.nom, x.data_neixement )
criteri_cognom_i_data = lambda x: u"{0}{1}".format( x.cognoms, x.data_neixement )

criteri = criteri_cognom_i_data

for x in a:
  x.ss = slugify( criteri(x) )

for x in a:
     repetits = [ y for y in a if y.ss == x.ss and y.id != x.id and y.id !=  544 ]  # and not y.data_baixa
     if repetits and all( [ (x.id < r.id) for r in repetits ] ) and x.data_baixa:
        print (x.id, [ z.id for z in repetits ])
        print (x,  repetits) 
        f( x, repetits, c )
        

### ---- SQL ---- ###
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
    