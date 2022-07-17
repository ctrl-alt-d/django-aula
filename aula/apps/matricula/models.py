from django.db import models
from aula.apps.alumnes.models import Alumne, Curs
from aula.apps.sortides.models import Quota, QuotaPagament, return_any_actual
from aula.apps.extPreinscripcio.models import Preinscripcio
from private_storage.fields import PrivateFileField
from django.conf import settings
from aula.apps.matricula.business_rules.document import document_post_delete

class Matricula(models.Model):
    ESTAT_CHOICES=[
        ('A','Acceptada'),
        ('F','Finalitzada'),
        ]    
    BONIF_CHOICES=[
        ('0','Cap'),
        ('5','50%'),
        ('1','100%'),
        ]    
    CONF_CHOICES=[('C','Confirma matrícula'),('N','No confirma')]

    idAlumne=models.CharField("RALC de l'alumne", max_length=15)
    estat=models.CharField( max_length=1, choices=ESTAT_CHOICES, default='A')
    any=models.IntegerField(default=return_any_actual)
    curs = models.ForeignKey(Curs, verbose_name="Curs on matricular-se", on_delete=models.PROTECT)
    quota=models.ForeignKey(Quota, on_delete=models.PROTECT, null=True, blank=True)
    alumne=models.ForeignKey(Alumne, related_name='matricula', on_delete=models.PROTECT, null=True, blank=True)
    preinscripcio=models.ForeignKey(Preinscripcio, on_delete=models.PROTECT, null=True, blank=True)
    acceptar_condicions=models.BooleanField("Accepto condicions de matrícula")
    acceptacio_en=models.DateTimeField(null=True)
    confirma_matricula=models.CharField("Confirmo matrícula", max_length=1, choices=CONF_CHOICES, null=True, blank=True)
    curs_complet=models.BooleanField("Matrícula del curs complet", help_text = 'Matrícula típica de totes les UFs', default=False)
    quantitat_ufs=models.IntegerField("UFs soltes, curs no complet", null=True, blank=True, default=0)
    llistaufs = models.CharField("Mòduls i ufs de la matrícula", help_text = 'En cas d\'UFs soltes', max_length=250, null=True, blank=True)
    bonificacio=models.CharField("Tipus de bonificació taxes", max_length=1, choices=BONIF_CHOICES, default='0')
    fracciona_taxes=models.BooleanField("Fracciona pagament taxes", default=False)
    nom = models.CharField("Nom alumne",max_length=50, default='')
    cognoms = models.CharField("Cognoms alumne",max_length=100, default='')
    centre_de_procedencia = models.CharField("Centre de procedència", max_length=50, null=True, blank=True)
    data_naixement = models.DateField("Data de naixement", default=None)
    alumne_correu = models.EmailField("Correu de l'alumne", help_text = u'Correu de notificacions de l\'alumne', null=True)
    adreca = models.CharField("Adreça", max_length=250, default='')
    localitat = models.CharField("Localitat", max_length=250, default='')
    cp = models.CharField("Codi postal", max_length=10, default='')
    rp1_nom = models.CharField("Nom complet 1r responsable", max_length=250, default='') #responsable 1
    rp1_telefon = models.CharField("Telèfon 1r responsable", max_length=15, default='')
    rp1_correu = models.EmailField( "Correu 1r responsable", default='')
    rp2_nom = models.CharField("Nom complet 2n responsable", max_length=250, null=True, blank=True) #responsable 2
    rp2_telefon = models.CharField("Telèfon 2n responsable", max_length=15, null=True, blank=True)
    rp2_correu = models.EmailField( "Correu 2n responsable", null=True, blank=True)

    class Meta:
        verbose_name = u'Matrícula'
        verbose_name_plural = u'Matrícules' 
              
    def __str__(self):
        return str(self.alumne)+' '+str(self.any)+' '+str(self.curs)
    
    @property
    def pagamentFet(self):
        pag=self.getPagament
        if pag:
            for p in pag:
                if not p.pagamentFet: return False
            return True
        return False
    
    @property
    def getPagament(self):
        if not self.quota:
            p=QuotaPagament.objects.filter(alumne=self.alumne, quota__any=self.any, quota__tipus__nom=settings.CUSTOM_TIPUS_QUOTA_MATRICULA)
        else:
            p=QuotaPagament.objects.filter(alumne=self.alumne, quota=self.quota)
        return p

class Document(models.Model):
    fitxer = PrivateFileField("Fitxer amb documents", upload_to='matricula/%Y/', 
                              max_file_size=settings.FILE_UPLOAD_MAX_MEMORY_SIZE, null=True)
    matricula=models.ForeignKey(Matricula, on_delete=models.PROTECT,  blank=True, null=True)
    
    class Meta:
        verbose_name = u'Document'
        verbose_name_plural = u'Documents' 
              
    def __str__(self):
        return str(self.fitxer.name) + ((' '+str(self.matricula)) if self.matricula else '')

from django.db.models.signals import post_delete
post_delete.connect(document_post_delete, sender = Document )
