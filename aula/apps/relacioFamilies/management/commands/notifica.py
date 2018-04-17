# This Python file uses the following encoding: utf-8

from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from aula.apps.relacioFamilies.notifica import notifica

class Command(BaseCommand):
    help = "Notifica a les families"

    def handle(self, *args, **options):

        try:
            self.stdout.write(u"Iniciant procés notificacions" )
            notifica()
            self.stdout.write(u"Fi procés notificacions" )
        except Exception, e:
            self.stdout.write(u"Error al procés notificacions: {0}".format( unicode(e) ) )
            errors = [unicode(e)]            
         
            #Deixar missatge a la base de dades (utilitzar self.user )
            from aula.apps.missatgeria.models import Missatge
            from django.contrib.auth.models import User, Group
     
            usuari_notificacions, new = User.objects.get_or_create( username = 'TP')
            if new:
                usuari_notificacions.is_active = False
                usuari_notificacions.first_name = u"Usuari Tasques Programades"
                usuari_notificacions.save()
            msg = Missatge( 
                        remitent= usuari_notificacions, 
                        text_missatge = u"Error enviant notificacions relació famílies.")    
            importancia = 'VI' 
             
            administradors, _ = Group.objects.get_or_create( name = 'administradors' )
             
            msg.envia_a_grup( administradors , importancia=importancia)
            msg.afegeix_errors( errors )
            
            