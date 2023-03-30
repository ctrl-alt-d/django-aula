# This Python file uses the following encoding: utf-8

from django.db import models
#from django.db.models import get_model
from django.contrib.auth.models import User
from aula.utils.tools import unicode
import uuid
from django.utils.crypto import get_random_string

#-------------------------------------------------------------

class AbstractDepartament(models.Model):
    codi = models.CharField(max_length=4 )
    nom = models.CharField(max_length=300 )

    class Meta:
        abstract = True
        ordering = ['nom', ]
        verbose_name = u"Departament Didàctic"
        verbose_name_plural = u"Departaments Didàctics"        

    def __str__(self):
        return unicode( self.nom )

#----------------------------------------------------------------------------------------------

class AbstractAccio(models.Model):
    TIPUS_ACCIO_CHOICES = (
        ('PL','Passar llista'),
        ('LL','Posar o treure alumnes a la llista'),
        ('IN','Posar o treur Incidència'),
        ('EE','Editar Expulsió'),
        ('EC','Expulsar del Centre'),
        ('RE','Recullir expulsió'),
        ('AC','Registre Actuació'),
        ('AG','Actualitza alumnes des de Saga'),
        ('MT','Envia missatge a tutors' ),
        ('SK','Sincronitza Kronowin'),
        ('JF','Justificar Faltes'),        
        ('NF','Notificacio Families'),        
        ('AS','Accés a dades sensibles'),
        ('SU','Sincronitza Untis'),
        ('DS','Control Delivery Status Notification'),
    )
    tipus = models.CharField(max_length=2, choices=TIPUS_ACCIO_CHOICES)
    usuari = models.ForeignKey( User, db_index = True, related_name = 'usuari', on_delete=models.CASCADE )
    impersonated_from = models.ForeignKey( User, blank = True, null = True, related_name = 'impersonate_from', on_delete=models.CASCADE )
    moment = models.DateTimeField( auto_now_add = True,  db_index = True )
    l4 = models.BooleanField( default = False )
    text = models.TextField( )
    class Meta:
        abstract = True
        verbose_name = u"Acció d'usuari"
        verbose_name_plural = u"Accions d'usuari"
    def __str__(self):
        txt_imp = u'({0})'.format(self.impersonated_from) if self.impersonated_from else ''
        return u'{0} {1} {2} {3}'.format( self.moment, self.tipus, self.usuari, txt_imp )
    
#----------------------------------------------------------------------------------------------

class AbstractLoginUsuari(models.Model):   
    exitos = models.BooleanField()
    usuari = models.ForeignKey( User, db_index = True, related_name = 'LoginUsuari', on_delete=models.CASCADE )
    moment = models.DateTimeField( auto_now_add = True,  db_index = True )
    ip = models.CharField( max_length = 15, blank = True )
    class Meta:
        abstract = True
        ordering = ['usuari', '-moment']
        verbose_name = u"Login d'usuari"
        verbose_name_plural = u"Login d'usuari"
    #cal crear index a mà: create index login_usuar_u_m_idx1 on login_usuari ( usuari_id , moment desc );

class AbstractOneTimePasswd(models.Model):
    usuari = models.ForeignKey( User, db_index = True, on_delete=models.CASCADE)
    moment_expedicio = models.DateTimeField( auto_now_add = True )
    clau = models.CharField(max_length=40 )
    reintents = models.IntegerField( default = 0 )
    #    class Meta:                            <--- TODO: hauria de tenir abstract i no ho té.
    #        abstract = True                    <--- Caldrà arreglar-ho amb migracions.

class AbstractQRPortal(models.Model):
    alumne_referenciat = models.ForeignKey( "alumnes.Alumne", db_index = True,
                                            related_name="qr_portal_set",
                                            related_query_name="qr_portal" , on_delete=models.CASCADE)
    usuari_referenciat = models.OneToOneField( User, db_index = True, blank = True, null = True, on_delete=models.CASCADE)
    moment_expedicio = models.DateTimeField( auto_now_add = True )
    moment_captura = models.DateTimeField( blank = True, null = True, unique = True )
    moment_confirmat_pel_tutor = models.DateTimeField(blank=True, null=True)
    darrera_sincronitzacio = models.DateTimeField( blank = True, null = True )
    novetats_detectades_moment = models.DateTimeField( blank = True, null = True  )
    clau = models.CharField(max_length=40, db_index=True)
    numero_de_mobil = models.CharField(max_length=40, blank = True )
    localitzador = models.CharField(max_length=4, unique=True, default="-", db_index=True)
    es_el_token_actiu = models.BooleanField(default=False)

    def calcula_clau_i_localitzador(self):
        for _ in range(100):
            self.clau = str(uuid.uuid4())
            self.localitzador = get_random_string(length=4)
            clau_unica = not self.__class__.objects.filter(clau=self.clau).exists()
            loca_unica = not self.__class__.objects.filter(localitzador=self.localitzador).exists()
            if clau_unica and loca_unica:
                return
        raise Exception("Impossible, ens hem quedat sense codis app")

    class Meta:
        abstract = True