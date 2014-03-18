update alumnes_alumne 
   set cognoms = 'c' || (id * 7777) % 27762 ,   
           nom = 'c' || ( (id * 7777) %  17775 ),
           correu_tutors = 'c' || ( (id * 7777) %  17775 ),
           correu_relacio_familia_pare = 'c' || ( (id * 7777) %  17775 ),
           correu_relacio_familia_mare = 'c' || ( (id * 7777) %  17775 ),
           centre_de_procedencia = 'c' || ( (id * 7777) %  17775 ),
           telefons = 'c' || ( (id * 7777) %  17775 ),
           tutors = 'c' || ( (id * 7777) %  17775 ),
           adreca = 'c' || ( (id * 7777) %  17775 );
           
update incidencies_expulsio set motiu = 'c' || (id * 7777) % 27762 ;         

truncate table  tutoria_actuacio cascade;
truncate table tutoria_cartaabsentisme cascade;
truncate table tutoria_resumanualalumne cascade;
truncate table tutoria_seguimenttutorialrespostes cascade;
truncate table tutoria_seguimenttutorial cascade;
truncate table incidencies_sancio cascade;

