# This Python file uses the following encoding: utf-8

from django.db import models
from datetime import date

from django.templatetags.static import static
from datetime import datetime
from private_storage.fields import PrivateFileField

from aula.apps.usuaris.models import Professor, AlumneUser
from aula.apps.tutoria.models import SeguimentTutorial
from aula.apps.alumnes.named_instances import Nivells_no_obligatoris, Cursa_nivell
from django.utils import timezone
#  amorilla@xtec.cat
from django.conf import settings
import calendar
from dateutil.relativedelta import relativedelta

from aula.settings import CUSTOM_TIPUS_MIME_FOTOS
from django.contrib.auth.models import User

class AbstractNivell(models.Model):
    nom_nivell = models.CharField("Nom nivell",max_length=45, unique=True)
    ordre_nivell =  models.IntegerField(null=True, blank=True,help_text=u"S\'utilitza per mostrar un nivell abans que un altre (Ex: ESO=0, CFSI=1000)")
    descripcio_nivell = models.CharField(max_length=240, blank=True)
    anotacions_nivell = models.TextField(blank=True)
    matricula_oberta = models.BooleanField("Matrícula oberta", default=False)
    limit_matricula = models.DateField("Límit matrícula", null=True, blank=True, help_text=u"Dia límit per fer confirmació de matrícula")
    taxes = models.ForeignKey('sortides.TipusQuota', on_delete=models.PROTECT, blank=True, null=True, default=None)
    preexclusiva = models.BooleanField("Matrícula exclusiva de Preinscripció", default=False)
    
    class Meta:
        abstract = True        
        ordering = ['ordre_nivell']
        verbose_name = u'Nivell'
        verbose_name_plural = u'Nivells'
    def __str__(self):
        return self.nom_nivell + ' (' + self.descripcio_nivell + ')'
    def save(self, *args, **kwargs):
        super(AbstractNivell, self).save(*args, **kwargs) # Call the "real" save() method.
    
    #amorilla@xtec.cat
    # Retorna el nivell que correspon segons CUSTOM_NIVELLS
    # Si no correspon cap aleshores retorna el nom_nivell original
    def getNivellCustom(self):
        for k,v in settings.CUSTOM_NIVELLS.items():
            if self.nom_nivell in v:
                return k
        return self.nom_nivell
    

class AbstractCurs(models.Model):
    nivell = models.ForeignKey("alumnes.Nivell", on_delete=models.CASCADE)
    nom_curs = models.CharField("Nom curs",max_length=45, help_text=u"Un número que representa el curs (Ex: 3)")
    nom_curs_complert = models.CharField(max_length=45, blank=True, unique=True, help_text=u"Dades que es mostraran (Ex: 1r ESO)")
    data_inici_curs = models.DateField("Comencen", null=True, blank=True, help_text=u"Dia que comencen les classes (cal informar aquest cap per poder fer control de presència)")
    data_fi_curs = models.DateField("Acaben", null=True, blank=True, help_text=u"Dia que finalitzen les classes (es poden posar dies festius a l\'apartat corresponent)")
    confirmacio_oberta = models.BooleanField("Confirmació activada", default=False)
    limit_confirmacio = models.DateField("Límit confirmació", null=True, blank=True, help_text=u"Dia límit per fer confirmació de matrícula")
    
    class Meta:
        abstract = True        
        #order_with_respect_to = 'nivell'
        ordering = ['nivell','nom_curs']
        verbose_name = u'Curs'
        verbose_name_plural = u'Cursos'
        unique_together = ("nivell","nom_curs",)

    def save(self, *args, **kwargs):
        super(AbstractCurs, self).save(*args, **kwargs) # Call the "real" save() method.
    
    def __str__(self):
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
    curs = models.ForeignKey("alumnes.Curs", on_delete=models.CASCADE)
    nom_grup = models.CharField(max_length=45, help_text=u'''Això normalment serà una lletra. Ex 'A' ''')
    descripcio_grup = models.CharField(max_length=240, blank=True)
    class Meta:
        abstract = True        
        ordering = ['curs','curs__nivell__nom_nivell', 'curs__nom_curs', 'nom_grup']
        verbose_name = u'Grup'
        verbose_name_plural = u'Grups'
    def __str__(self):
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
                ('MAN','Alumne donat d\'alta manualment'),
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

    PRIMER_RESPONSABLE = (
        (0, 'Responsable 1'),
        (1, 'Responsable 2'),
    )

    ralc = models.CharField(max_length=100, blank=True, db_index=True)
    grup = models.ForeignKey("alumnes.Grup", on_delete=models.CASCADE)
    nom = models.CharField("Nom",max_length=240)
    nom_sentit = models.CharField(
        "Nom Sentit",max_length=240,
        blank=True,
        help_text="És el nom amb el que l'alumne se sent identificat "
                  "tot i que formalment encara els tràmits de canvi de"
                  " nom no estiguin completats"
    )
    cognoms = models.CharField("Cognoms",max_length=240)
    data_neixement = models.DateField("Data naixement",null=True)
    estat_sincronitzacio = models.CharField(choices=ESTAT_SINCRO_CHOICES ,max_length=3, blank=True)

    #DEPRECATED vvv
    correu_tutors = models.CharField(max_length=240, blank=True)
    correu_relacio_familia_pare =  models.EmailField( u'1r Correu Notifi. Tutors', help_text = u'Correu de notificacions de un tutor', blank=True)
    correu_relacio_familia_mare =  models.EmailField( u'2n Correu Notifi. Tutors', help_text = u"Correu de notificacions de l'altre tutor (opcional)", blank=True)
    #DEPRECATED ^^^

    motiu_bloqueig = models.CharField(max_length=250, blank=True)

    #DEPRECATED vvv
    tutors_volen_rebre_correu = models.BooleanField()
    #DEPRECATED ^^^

    centre_de_procedencia = models.CharField(max_length=250, blank=True)
    localitat = models.CharField(max_length=240, blank=True)
    municipi = models.CharField(max_length=240, blank=True)
    cp = models.CharField(max_length=240, blank=True)
    telefons = models.CharField(max_length=250, blank=True, db_index=True)
    tutors = models.CharField(max_length=250, blank=True)
    adreca = models.CharField(max_length=250, blank=True)
    correu = models.CharField(max_length=240, blank=True)

    #DEPRECATED vvv
    rp1_nom = models.CharField(max_length=250, blank=True) #responsable 1
    rp1_telefon = models.CharField(max_length=250, blank=True, db_index=True)
    rp1_mobil = models.CharField(max_length=250, blank=True, db_index=True)
    rp1_correu = models.CharField(max_length=240, blank=True)
    rp2_nom = models.CharField(max_length=250, blank=True) #responsable 2
    rp2_telefon = models.CharField(max_length=250, blank=True, db_index=True)
    rp2_mobil = models.CharField(max_length=250, blank=True, db_index=True)
    rp2_correu = models.CharField(max_length=240, blank=True)
    #DEPRECATED ^^^

    responsable_preferent = models.ForeignKey("relacioFamilies.Responsable", null=True, on_delete=models.SET_NULL, help_text = u"Responsable preferent de l'alumne/a")

    #DEPRECATED vvv
    primer_responsable = models.IntegerField( choices = PRIMER_RESPONSABLE, blank=False,
                                               default = 0,
                                               help_text = u"Principal responsable de l'alumne/a")
    #DEPRECATED ^^^

    altres_telefons = models.CharField(max_length=250, blank=True)

    data_alta = models.DateField( default = timezone.now, null=False )
    data_baixa = models.DateField( null=True, blank = True )
    
    user_associat = models.OneToOneField(  AlumneUser , null=True, on_delete=models.SET_NULL,  )

    usuaris_app_associats = models.ManyToManyField(User, through="usuaris.QRPortal",
                                                   related_name="alumne_app_set",
                                                   related_query_name="alumne_app")
    #DEPRECATED vvv
    relacio_familia_darrera_notificacio = models.DateTimeField( null=True, blank = True )
    #DEPRECATED ^^^

    
    periodicitat_faltes = models.IntegerField( choices = PERIODICITAT_FALTES_CHOICES, blank=False,
                                               default = 1,
                                               help_text = u'Interval de temps mínim entre dues notificacions')
  
    periodicitat_incidencies = models.BooleanField( choices = PERIODICITAT_INCIDENCIES_CHOICES, blank=False,
                                               default = True,
                                               help_text = u'Periodicitat en la notificació de les incidències.'
                                                )


    foto = PrivateFileField("Foto", upload_to='alumnes/fotos', content_types=CUSTOM_TIPUS_MIME_FOTOS, max_file_size=3145728, null=True, blank=True)
    observacions =models.TextField(max_length=150, null=True, blank=True, help_text= u"Informació visible pels seus professors/es")

    class Meta:
        abstract = True
        ordering = ['grup','cognoms','nom']
        verbose_name = u'Alumne'
        verbose_name_plural = u'Alumnes'
        unique_together = [] #("nom", "cognoms",  "data_neixement", "grup__curs__nivell"),("ralc","grup__curs__nivell"))

    def __str__(self):
        return (u'És baixa: ' if self.esBaixa() else u'') +  self.cognoms + ', ' + self.nom 

    def get_nom_sentit(self):
        return (u'És baixa: ' if self.esBaixa() else u'') +  self.cognoms + ', ' + (self.nom_sentit or self.nom )

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

    def tutorsIndividualitzatsDeLAlumne(self):
        from django.db.models import Q
        q_tutors_individualitat = Q( tutorindividualitzat__alumne = self )
        return Professor.objects.filter(q_tutors_individualitat ).distinct()

    def tutorsDelGrupDeLAlumne(self):
        return Professor.objects.filter(tutor__grup=self.grup).distinct()

    def tutorsDeLAlumne_display(self):
        return u", ".join( [str(tutor) for tutor in self.tutorsDeLAlumne() ])

    def force_delete(self):
        super(AbstractAlumne,self).delete()
        
    def esta_relacio_familia_actiu(self):
        # TODO majors o menors d'edat
        TeCorreuPare_o_Mare = bool(self.get_correus_relacio_familia())
        usuariActiu = self.get_user_associat() is not None and self.user_associat.is_active
        usuariActiu = usuariActiu or any(self.responsablesActius())
        return TeCorreuPare_o_Mare and usuariActiu
    
    def responsablesActius(self):
        return [ x.get_user_associat() is not None and x.user_associat.is_active for x in self.get_responsables() if x ]
    
    def get_correu(self):
        return self.correu
    
    def get_correus_relacio_familia(self):
        return [ x.correu_relacio_familia for x in self.get_responsables() if x and x.correu_relacio_familia ]

    def get_correus_tots(self):
        tots=self.get_correus_relacio_familia()
        tots=tots+[ x.correu for x in self.get_responsables() if x and x.correu ]
        tots=tots+[ self.get_correu() ]
        return tots
    
    def get_telefons(self):
        return [ t for t in [self.telefons, self.altres_telefons] if t ]
    
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

    def cursa_nivell(self, nivell_txt):
        return Cursa_nivell(nivell_txt, self)
    
    #amorilla@xtec.cat
    # Retorna el nivell que correspon a l'alumne segons CUSTOM_NIVELLS
    # Si no correspon cap aleshores retorna el nivell assignat a la base de dades
    def getNivellCustom(self):
        for k,v in settings.CUSTOM_NIVELLS.items():
            if self.grup.curs.nivell.nom_nivell in v:
                return k
        return self.grup.curs.nivell.nom_nivell

    # amorilla@xtec.cat  
    # Retorna l'edat de l'alumne. 
    # Si s'indica una data per paràmetre retorna l'edat en la data indicada, 
    # en altre cas calcula l'edat en el dia actual
    def edat( self, data=None):
        if data is None:
            data = date.today()
        dnaix = self.data_neixement
        return relativedelta(data, dnaix).years

    # amorilla@xtec.cat 
    # Retorna true si és l'aniversari de l'alumne. 
    # Té en compte el cas 29/2, si l'any no té 29/2 indica aniversari el 28/2.
    # Si s'indica una data per paràmetre retorna si és aniversari en la data indicada, 
    # en altre cas calcula en el dia actual
    def aniversari( self, data=None):
        if data is None:
            data = date.today()
        dnaix = self.data_neixement
        return  (( data.month,  data.day) == (dnaix.month, dnaix.day)) or (not calendar.isleap(data.year) and (dnaix.month, dnaix.day) ==(2,29) and ( data.month,  data.day)==(2,28) )

    @property
    def get_foto_or_default(self):
        foto = self.foto.url if self.foto else static('nofoto.png')
        return foto
    
    def get_responsables(self, rp1_dni=None, rp2_dni=None):
        '''
        Selecciona els responsables de l'alumne que corresponen
        als dnis indicats.
        Si no s'aporten els dnis, selecciona els responsables
        existents de l'alumne, en aquest cas el primer és el preferent.
        retorna els 2 responsables, poden ser None si no existeixen.
        '''
        if not bool(rp1_dni) and not bool(rp2_dni):
            responsables=list(self.responsables.all())
            # Ha de retornar 2 elements, afegeix None
            for i in range(len(responsables),2):
                responsables.append(None)
            if self.responsable_preferent and responsables[0]!=self.responsable_preferent and responsables[1]:
                responsables.reverse()
            return responsables
        resp1=self.responsables.filter(dni=rp1_dni).first()
        resp2=self.responsables.filter(dni=rp2_dni).first()
        return resp1, resp2
    
    def get_dades_responsables(self):
        dades={}
        resp1, resp2 = self.get_responsables()
        dades['respPre']=resp1.get_dades() if resp1 else ''
        dades['respAlt']=resp2.get_dades() if resp2 else ''
        return dades
    
    def esborraAntics_responsables(self, dnis):
        '''
        Elimina altres responsables anteriors, només
        conserva els que corresponen a la llista de dnis.
        Els responsables sense alumnes queden com a baixa.
        dnis list amb els dnis vàlids de responsables
        '''
        for r in self.responsables.exclude(dni__in=dnis):
            r.alumnes_associats.remove(self)
            if not r.alumnes_associats.exists():
                # Fa baixa si el responsable es queda sense alumnes
                r.delete()

class AbstractDadesAddicionalsAlumne(models.Model):

    alumne = models.ForeignKey('alumnes.Alumne', on_delete=models.CASCADE)
    label = models.CharField(max_length=50, help_text=u"Nom del camp addicional")
    value = models.CharField(max_length=500, blank=True, null=True, help_text="Contingut del camp addicional")

    class Meta:
        abstract = True
        verbose_name = u"Dada addicional de l'alumne"
        verbose_name_plural = u"Dades addicionals dels alumnes"
        unique_together = ['alumne','label']

    def __str__(self):
        return self.alumne.cognoms + ', ' + self.alumne.nom + ' - ' + self.label + ': ' + self.value
