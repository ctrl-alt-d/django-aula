# This Python file uses the following encoding: utf-8
from aula.apps.tutoria.abstract_models import AbstractSeguimentTutorial,\
    AbstractResumAnualAlumne, AbstractSeguimentTutorialPreguntes,\
    AbstractSeguimentTutorialRespostes, AbstractActuacio, AbstractTutor,\
    AbstractTutorIndividualitzat, AbstractCartaAbsentisme
from aula.apps.tutoria.business_rules.actuacio import actuacio_clean,\
    actuacio_pre_delete, actuacio_pre_save, actuacio_post_save
from aula.apps.tutoria.business_rules.cartaaabsentisme import cartaabsentisme_clean

class SeguimentTutorial(AbstractSeguimentTutorial):
    pass

class ResumAnualAlumne(AbstractResumAnualAlumne):
    pass

class SeguimentTutorialPreguntes(AbstractSeguimentTutorialPreguntes):
    pass

class SeguimentTutorialRespostes(AbstractSeguimentTutorialRespostes):
    pass

#----------------------------------------------------------------------------------------------------------

class Actuacio(AbstractActuacio):
    def clean(self):
        actuacio_clean(self)

class Tutor(AbstractTutor):
    pass

class TutorIndividualitzat(AbstractTutorIndividualitzat):
    pass

#----------------------------------------------------------

class CartaAbsentisme(AbstractCartaAbsentisme):
    def clean(self):
        cartaabsentisme_clean( self )

#----------------------------------------------------------

from django.db.models.signals import post_save, pre_save, pre_delete

#actuacio
pre_delete.connect(actuacio_pre_delete, sender= Actuacio)    
pre_save.connect(actuacio_pre_save, sender = Actuacio )
post_save.connect(actuacio_post_save, sender = Actuacio )






