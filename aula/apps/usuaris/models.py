# This Python file uses the following encoding: utf-8

from django.db import models
#from django.db.models import get_model
from django.contrib.auth.models import User, Group
from aula.apps.usuaris.abstract_usuaris import AbstractDepartament,\
    AbstractAccio, AbstractLoginUsuari, AbstractOneTimePasswd

#-------------------------------------------------------------

class Departament(AbstractDepartament):
    pass
#-------------------------------------------------------------

class AlumneUserManager(models.Manager):
    def get_query_set(self):
        grupAlumnes, _ = Group.objects.get_or_create( name = 'alumne' )
        return super(AlumneUserManager, self).get_query_set().filter( groups = grupAlumnes   )


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
                        
    def __unicode__(self):
        return unicode( self.getAlumne() )
     

#----------------------------------------------------------------------------------------------

class ProfessorManager(models.Manager):
    def get_query_set(self):
        grupProfessors, _ = Group.objects.get_or_create( name = 'professors' )
        return super(ProfessorManager, self).get_query_set().filter( groups = grupProfessors   )

class Professor(User):
    objects = ProfessorManager()
    class Meta:
        proxy = True
        ordering = ['last_name','first_name','username']

    def getUser(self):
        return User.objects.get( pk = self.pk )
    
    def nMissatgesNoLlegits(self):
        self.destinatari_set.filter( moment_lectura__isnull = True ).count()
                    
    def __unicode__(self):
        nom = self.first_name + u' ' + self.last_name if self.last_name else self.username 
        return nom.title()  
     
def User2Professor( user ):
    professor = None
    try:
        professor = Professor.objects.get( pk = user.pk )
    except:
        pass
    return professor

#----------------------------------------------------------------------------------------------

class ProfessionalManager(models.Manager):
    def get_query_set(self):
        grupProfessional, _ = Group.objects.get_or_create( name = 'professional' )
        return super(ProfessionalManager, self).get_query_set().filter( groups = grupProfessional   )

class Professional(User):
    objects = ProfessionalManager()
    class Meta:
        proxy = True
        ordering = ['last_name','first_name','username']

    def getUser(self):
        return User.objects.get( pk = self.pk )
                    
    def __unicode__(self):
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

class LoginUsuari(AbstractLoginUsuari):
    pass   

class OneTimePasswd(AbstractOneTimePasswd):
    pass

