# This Python file uses the following encoding: utf-8
import uuid
from django.db import models
#from django.db.models import get_model
from django.contrib.auth.models import User, Group
from aula.apps.usuaris.abstract_usuaris import AbstractDepartament,\
    AbstractAccio, AbstractLoginUsuari, AbstractOneTimePasswd, AbstractQRPortal, AbstractNotifUsuari
from aula.utils.tools import unicode
from aula.settings import CUSTOM_TIPUS_MIME_FOTOS
from private_storage.fields import PrivateFileField
from django.templatetags.static import static
#-------------------------------------------------------------

class Departament(AbstractDepartament):
    pass
#-------------------------------------------------------------

class AlumneUserManager(models.Manager):
    def get_queryset(self):
        grupAlumnes, _ = Group.objects.get_or_create( name = 'alumne' )
        return super(AlumneUserManager, self).get_queryset().filter( groups = grupAlumnes, username__startswith='almn' )


class AlumneUser(User):
    objects = AlumneUserManager()
    class Meta:
        proxy = True
        ordering = ['last_name','first_name','username']

    def getUser(self):
        return User.objects.get( pk = self.pk )

    def getAlumne(self):
        alumne = None
        try:
            alumne = self.alumne
        except:
            pass
        return alumne
                        
    def __str__(self):
        return unicode( self.getAlumne() )

def User2Alumne(user):
    from aula.apps.alumnes.models import Alumne
    alumne = None
    try:
        alumne = Alumne.objects.get(user_associat=user)
    except:
        pass
    return alumne

# ----------------------------------------------------------------------------------------------

class ResponsableUserManager(models.Manager):
    def get_queryset(self):
        grupAlumnes, _ = Group.objects.get_or_create( name = 'alumne' )
        return super().get_queryset().filter( groups = grupAlumnes, username__startswith='resp' )

class ResponsableUser(User):
    objects = ResponsableUserManager()
    class Meta:
        proxy = True
        ordering = ['last_name','first_name','username']
    
    def getUser(self):
        return User.objects.get( pk = self.pk )
    
    def getResponsable(self):
        responsable = None
        try:
            responsable = self.responsable
        except:
            pass
        return responsable
    
    def __str__(self):
        return self.getResponsable()

def User2Responsable(user):
    from aula.apps.relacioFamilies.models import Responsable
    responsable = None
    try:
        responsable = Responsable.objects.get(user_associat=user)
    except:
        pass
    return responsable

    # ----------------------------------------------------------------------------------------------

class ProfessorManager(models.Manager):
    def get_queryset(self):
        #grupProfessors, _ = Group.objects.get_or_create(name='professors')
        #return super(ProfessorManager, self).get_queryset().filter(groups=grupProfessors)

        grupProfessors = 'professors'
        return super(ProfessorManager, self).get_queryset().filter(groups__name=grupProfessors)


class Professor(User):
    objects = ProfessorManager()

    class Meta:
        proxy = True
        ordering = ['last_name', 'first_name', 'username']

    def getUser(self):
        return User.objects.get(pk=self.pk)

    def nMissatgesNoLlegits(self):
        self.destinatari_set.filter(moment_lectura__isnull=True).count()

    def __str__(self):
        nom = self.first_name + u' ' + self.last_name if self.last_name else self.username
        return nom.title()

def User2Professor(user):
    professor = None
    try:
        professor = Professor.objects.get(pk=user.pk)
    except:
        pass
    return professor

class DadesAddicionalsProfessor(models.Model):
    clauDeCalendari = models.UUIDField(default=uuid.uuid4)
    professor = models.OneToOneField(Professor, on_delete=models.CASCADE)
    foto = PrivateFileField("Foto", upload_to='profes/fotos', content_types=CUSTOM_TIPUS_MIME_FOTOS,
                            max_file_size=3145728, null=True, blank=True)

    @property
    def get_foto_or_default(self):
        foto = self.foto.url if self.foto else static('nofoto.png')
        return foto

def GetDadesAddicionalsProfessor(professor):
    dadesAddicionals, created = DadesAddicionalsProfessor.objects.get_or_create(
        professor = professor, 
        defaults={ },
        )
    if created:
        professor.refresh_from_db()
    return dadesAddicionals



# ----------------  ------------------------------------------------------------------------------

class ProfessorConsergeManager(models.Manager):
    def get_queryset(self):
        #grupProfessors, _ = Group.objects.get_or_create(name='professors')
        #grupConsergeria, _ = Group.objects.get_or_create(name='consergeria')
        grupProfessors = 'professors'
        grupConsergeria = 'consergeria'
        return super(ProfessorConsergeManager, self).get_queryset().filter(groups__name__in=[grupProfessors, grupConsergeria]).distinct()

class ProfessorConserge(User):
    objects = ProfessorConsergeManager()

    class Meta:
        proxy = True
        ordering = ['last_name', 'first_name', 'username']

    def getUser(self):
        return User.objects.get(pk=self.pk)

    def nMissatgesNoLlegits(self):
        self.destinatari_set.filter(moment_lectura__isnull=True).count()

    def __str__(self):
        nom = u"{} {}".format( self.first_name, self.last_name ) if self.last_name else self.username
        rol = u" (consergeria)" if self.groups.filter(name="consergeria").exists() else u" (professorat)"
        nom += rol
        return nom

def User2ProfessorConserge(user):
    professor = None
    try:
        professor = ProfessorConserge.objects.get(pk=user.pk)
    except:
        pass
    return professor


#----------------------------------------------------------------------------------------------

class ProfessionalManager(models.Manager):
    def get_queryset(self):
        grupProfessional, _ = Group.objects.get_or_create( name = 'professional' )
        return super(ProfessionalManager, self).get_queryset().filter( groups = grupProfessional   )

class Professional(User):
    objects = ProfessionalManager()
    class Meta:
        proxy = True
        ordering = ['last_name','first_name','username']

    def getUser(self):
        return User.objects.get( pk = self.pk )
                    
    def __str__(self):
        nom = self.first_name + u' ' + self.last_name if self.last_name else self.username 
        return nom.title() 

def User2Professional( user ):
    professional = None
    try:
        professional = Professional.objects.get( pk = user.pk )
    except:
        pass
    return professional

#----------------------------------------------------------------------------------------------

class Accio(AbstractAccio):
    pass
    
#----------------------------------------------------------------------------------------------

class NotifUsuari(AbstractNotifUsuari):
    pass

class LoginUsuari(AbstractLoginUsuari):
    pass   

class OneTimePasswd(AbstractOneTimePasswd):
    pass

class QRPortal(AbstractQRPortal):
    pass