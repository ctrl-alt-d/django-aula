# This Python file uses the following encoding: utf-8

from django.db import models
from datetime import date
from django.utils.datetime_safe import datetime
from aula.apps.usuaris.models import Professor, AlumneUser
from aula.apps.tutoria.models import SeguimentTutorial
from aula.apps.alumnes.named_instances import Nivells_no_obligatoris

class AbstractNivell(models.Model):
    nom_nivell = models.CharField("Nom nivell",max_length=45, unique=True)
    ordre_nivell =  models.IntegerField(null=True, blank=True,help_text=u"S\'utilitza per mostrar un nivell abans que un altre (Ex: ESO=0, CFSI=1000)")
    descripcio_nivell = models.CharField(max_length=240, blank=True)
    anotacions_nivell = models.TextField(blank=True)
    class Meta:
        abstract = True        
        ordering = ['ordre_nivell']
        verbose_name = u'Nivell'
        verbose_name_plural = u'Nivells'
    def __unicode__(self):
        return self.nom_nivell + ' (' + self.descripcio_nivell + ')'
    def save(self, *args, **kwargs):
        super(AbstractNivell, self).save(*args, **kwargs) # Call the "real" save() method.

class AbstractCurs(models.Model):
    nivell = models.ForeignKey("alumnes.Nivell")
    nom_curs = models.CharField("Nom curs",max_length=45, help_text=u"Un número que representa el curs (Ex: 3)")
    nom_curs_complert = models.CharField(max_length=45, blank=True, unique=True, help_text=u"Dades que es mostraran (Ex: 1r ESO)")
    data_inici_curs = models.DateField("Comencen", null=True, blank=True, help_text=u"Dia que comencen les classes (cal informar aquest cap per poder fer control de presència)")
    data_fi_curs = models.DateField("Acaben", null=True, blank=True, help_text=u"Dia que finalitzen les classes (es poden posar dies festius a l\'apartat corresponent)")
    class Meta:
        abstract = True        
        #order_with_respect_to = 'nivell'
        ordering = ['nivell','nom_curs']
        verbose_name = u'Curs'
        verbose_name_plural = u'Cursos'
        unique_together = ("nivell","nom_curs",)

    def save(self, *args, **kwargs):
        super(AbstractCurs, self).save(*args, **kwargs) # Call the "real" save() method.
    
    def __unicode__(self):
        return self.nom_curs_complert
    
    def dies(self):
        if not (self.data_inici_curs and self.data_fi_curs):
            return []
        import datetime as t
        totsElsDies = []
        dia = self.data_inici_curs
        while dia <= self.data_fi_curs:
            delta = t.timedelta( days = +1)
            dia += delta
            totsElsDies.append(dia)
        return totsElsDies    

class AbstractGrup(models.Model):
    curs = models.ForeignKey("alumnes.Curs")
    nom_grup = models.CharField(max_length=45, help_text=u'''Això normalment serà una lletra. Ex 'A' ''')
    descripcio_grup = models.CharField(max_length=240, blank=True)
    class Meta:
        abstract = True        
        ordering = ['curs','curs__nivell__nom_nivell', 'curs__nom_curs', 'nom_grup']
        verbose_name = u'Grup'
        verbose_name_plural = u'Grups'
    def __unicode__(self):
        return self.descripcio_grup if self.descripcio_grup else self.curs.nom_curs_complert + ' ' + self.nom_grup

    def save(self, *args, **kwargs):
        #descripció és una mena de cache.
        if not self.descripcio_grup:
            self.descripcio_grup = self.curs.nom_curs_complert + ' ' + self.nom_grup
        super(AbstractGrup, self).save(*args, **kwargs) # Call the "real" save() method.      
     

#------------------------------------------------------------------------------------------------


#https://docs.djangoproject.com/en/dev/topics/db/managers/#django.db.models.Manager
#class AlumneManager(models.Manager):
#    def sincronitzaSaga(self,f, user):
#        import alumnes.sincronitzaSaga  as c
#        return c.sincronitza( f, user )

#------------------------------------------------------------------------------------------------

class AbstractAlumne(models.Model):
    ESTAT_SINCRO_CHOICES = (
                ('PRC', 'En procés de sincronització'),
                ('S-I', 'Sincronitzat Insert'),                            
                ('S-U', 'Sincronitzat Update'),                            
                ('DEL','Alumne donat de baixa'),
                            )
    PERIODICITAT_FALTES_CHOICES = (
                (0, 'No notificar'),
                (1, 'Un dia'),                            
                (2, 'Dos dies'),                            
                (3, 'Tres dies'),
                (7, 'Una setmana'),
                        )
 
    PERIODICITAT_INCIDENCIES_CHOICES = (
                (False, 'No notificar.'),
                (True,'Notificar-les totes.'),
            )
        
    grup = models.ForeignKey("alumnes.Grup")
    nom = models.CharField("Nom",max_length=240)
    cognoms = models.CharField("Cognoms",max_length=240)
    data_neixement = models.DateField(null=True)
    estat_sincronitzacio = models.CharField(choices=ESTAT_SINCRO_CHOICES ,max_length=3, blank=True)
    correu_tutors = models.CharField(max_length=240, blank=True)
    correu_relacio_familia_pare =  models.EmailField( u'1r Correu Notifi. Tutors', help_text = u'Correu de notificacions de un tutor', blank=True)
    correu_relacio_familia_mare =  models.EmailField( u'2n Correu Notifi. Tutors', help_text = u"Correu de notificacions de l'altre tutor (opcional)", blank=True)
    motiu_bloqueig = models.CharField(max_length=250, blank=True)
    tutors_volen_rebre_correu = models.BooleanField()
    centre_de_procedencia = models.CharField(max_length=250, blank=True)
    localitat = models.CharField(max_length=240, blank=True)
    telefons = models.CharField(max_length=250, blank=True, db_index=True)
    tutors = models.CharField(max_length=250, blank=True)
    adreca = models.CharField(max_length=250, blank=True)
    
    data_alta = models.DateField( default = date.today(), null=False )
    data_baixa = models.DateField( null=True, blank = True )
    
    user_associat = models.OneToOneField(  AlumneUser , null=True  )
    
    relacio_familia_darrera_notificacio = models.DateTimeField( null=True )
    
    periodicitat_faltes = models.IntegerField( choices = PERIODICITAT_FALTES_CHOICES, blank=False,
                                               default = 3,
                                               help_text = u'Interval de temps mínim entre dues notificacions')
  
    periodicitat_incidencies = models.BooleanField( choices = PERIODICITAT_INCIDENCIES_CHOICES, blank=False,
                                               default = 3,
                                               help_text = u'Periodicitat en la notificació de les incidències.'
                                                )


    
    class Meta:
        abstract = True        
        ordering = ['grup','cognoms','nom']
        verbose_name = u'Alumne'
        verbose_name_plural = u'Alumnes'
        unique_together = (("nom", "cognoms",  "data_neixement"))

    def __unicode__(self):
        return (u'És baixa: ' if self.esBaixa() else u'') +  self.cognoms + ', ' + self.nom 

    def delete(self):
        self.data_baixa = datetime.today()
        self.save()
        
    def esBaixa(self):
        return self.data_baixa is not None

    def tutorsDeLAlumne(self):
        from django.db.models import Q
        q_tutors_individualitat = Q( tutorindividualitzat__alumne = self )
        q_tutors_grup = Q( tutor__grup = self.grup )
        return Professor.objects.filter(q_tutors_individualitat | q_tutors_grup   ).distinct()

    def force_delete(self):
        super(AbstractAlumne,self).delete()
        
    def esta_relacio_familia_actiu(self):
        TeCorreuPare_o_Mare = self.correu_relacio_familia_pare  or self.correu_relacio_familia_mare 
        usuariActiu = self.get_user_associat() is not None and self.user_associat.is_active
        return True if TeCorreuPare_o_Mare and usuariActiu else False
    
    def get_correus_relacio_familia(self):
        return  [ x for x in [ self.correu_relacio_familia_pare, self.correu_relacio_familia_mare] if x  ]

    def get_user_associat(self):       
        return self.user_associat if self.user_associat_id is not None else None


    def get_seguiment_tutorial(self):       
        if not hasattr(self, 'seguimenttutorial'):
            a=self
            try:
                seguiment = SeguimentTutorial.objects.get( 
                    nom = a.nom,
                    cognoms = a.cognoms,
                    data_neixement = a.data_neixement,
                )
            except SeguimentTutorial.DoesNotExist:
                seguiment = SeguimentTutorial.objects.create( 
                    nom = a.nom,
                    cognoms = a.cognoms,
                    datadarreraactualitzacio = datetime.now()     ,                              
                    data_neixement = a.data_neixement,
                    informacio_de_primaria = '',
                    alumne= None
                )
            seguiment.alumne = a
            seguiment.save()    
            
            self.seguimenttutorial = seguiment       
            
        return self.seguimenttutorial
    
    def cursa_obligatoria(self):
        return self.grup.curs.nivell not in Nivells_no_obligatoris()







