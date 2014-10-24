select string_agg(id::text, ', ' order by id), max( a.nom || ' ' || a.cognoms)  , min( a.nom || ' ' || a.cognoms)  
    from alumnes_alumne a 
group by a.data_neixement, a.centre_de_procedencia , a.tutors, a.adreca
  having count(*) > 1;