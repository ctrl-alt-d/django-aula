from django.db import models
from private_storage.fields import PrivateFileField
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from aula.apps.alumnes.models import Alumne

class EmailPendent(models.Model):
    subject=models.TextField(null=True, blank=True)
    message=models.TextField(null=True, blank=True)
    fromemail=models.CharField(max_length=100, null=True, blank=True)
    toemail=models.TextField(null=True, blank=True)

    def __str__(self):
        pendents=list(eval(self.toemail)) if bool(self.toemail) else []
        pendents=pendents if len(pendents)<=2 else (str(pendents[0])+" i altres ... total:"+str(len(pendents)))
        return str(self.subject) + ': ' + str(self.fromemail) + '->' + str(pendents)

class DocAttach(models.Model):
    fitxer = PrivateFileField("Fitxer adjunt", upload_to='email/',
                              max_file_size=settings.FILE_UPLOAD_MAX_MEMORY_SIZE)
    email = models.ForeignKey(EmailPendent, on_delete=models.CASCADE, blank=True)
    
    class Meta:
        verbose_name = u'Attach File'
        verbose_name_plural = u'Attach Files'
        
    def __str__(self):
        return str(self.fitxer.name) + ((' '+str(self.email)) if self.email else '')

class Responsable(models.Model):
    from django.contrib.auth.models import User
    dni = models.CharField("Dni",max_length=10, unique=True)
    nom = models.CharField("Nom",max_length=240)
    cognoms = models.CharField("Cognoms",max_length=240)
    parentiu = models.CharField("Parentiu",max_length=20, blank=True)
    localitat = models.CharField(max_length=240, blank=True)
    municipi = models.CharField(max_length=240, blank=True)
    cp = models.CharField(max_length=240, blank=True)
    adreca = models.CharField(max_length=250, blank=True)
    telefon = models.CharField(max_length=250, blank=True, db_index=True)
    correu = models.CharField(max_length=240, blank=True)
    data_alta = models.DateField( default = timezone.now, null=False )
    data_baixa = models.DateField( null=True, blank = True )
    user_associat = models.OneToOneField(User , null=True, on_delete=models.SET_NULL)
    alumnes_associats = models.ManyToManyField(Alumne, related_name="responsables")
    correu_relacio_familia =  models.EmailField( u'Correu Notifi. Tutors', help_text = u'Correu de notificacions', blank=True)
    periodicitat_faltes = models.IntegerField( choices = Alumne.PERIODICITAT_FALTES_CHOICES, blank=False,
                                               default = 1,
                                               help_text = u'Interval de temps mínim entre dues notificacions')
    periodicitat_incidencies = models.BooleanField( choices = Alumne.PERIODICITAT_INCIDENCIES_CHOICES, blank=False,
                                               default = True,
                                               help_text = u'Periodicitat en la notificació de les incidències.'
                                                )
    motiu_bloqueig = models.CharField(max_length=250, blank=True)

    class Meta:
        ordering = ['cognoms','nom']
        verbose_name = u'Responsable'
        verbose_name_plural = u'Responsables'

    def __str__(self):
        return (u'És baixa: ' if self.esBaixa() else u'') +  self.cognoms + ', ' + self.nom +\
                    (u' (' + u' , '.join(filter(None, [self.telefon, self.correu_relacio_familia])) + u')')
    
    def delete(self):
        self.data_baixa = datetime.today()
        self.motiu_bloqueig = 'Baixa'
        self.user_associat.is_active=False
        self.user_associat.save()
        self.save()
        
    def esBaixa(self):
        return self.data_baixa is not None

    def force_delete(self):
        super().delete()
        
    def get_user_associat(self):
        return self.user_associat if self.user_associat_id is not None else None
    
    def get_alumnes_associats(self):
        return self.alumnes_associats.filter(data_baixa__isnull=True).order_by('cognoms','nom')
    
    def get_nom(self):
        return self.cognoms + ', ' + self.nom
    
    def get_telefon(self):
        return self.telefon
    
    def get_correu_importat(self):
        return self.correu
    
    def get_correu_relacio(self):
        return self.correu_relacio_familia
    
    def get_dades(self):
        return "{0} ({1},{2}) {3}".format(self.get_nom(), self.get_telefon(), self.get_correu_relacio(),
                        "Altres: {0}".format(self.get_correu_importat()) if bool(self.get_correu_importat()) and 
                                                    self.get_correu_importat()!=self.get_correu_relacio() else '')

from django.db.models.signals import post_delete, post_save
from aula.apps.relacioFamilies.business_rules.docattach import docattach_post_delete
from aula.apps.relacioFamilies.business_rules.responsable import responsable_post_save

post_delete.connect(docattach_post_delete, sender = DocAttach )
post_save.connect(responsable_post_save, sender = Responsable )
