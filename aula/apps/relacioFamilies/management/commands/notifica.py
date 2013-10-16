# This Python file uses the following encoding: utf-8

from django.core.management.base import BaseCommand, CommandError
from django.utils import translation
from aula.apps.relacioFamilies import notifica

class Command(BaseCommand):
    help = 'Notifica a les families'   

    def handle(self, *args, **options):

        try:
            notifica()
        except Exception, e:
            errors = [unicode(e)]
        
            #Deixar missatge a la base de dades (utilitzar self.user )
            from aula.apps.missatgeria.models import Missatge
            from django.contrib.auth.models import User, Group
    
            usuari_notificacions, new = User.objects.get_or_create( username = 'TP')
            if new:
                usuari_notificacions.is_active = False
                usuari_notificacions.first_name = u'Usuari Tasques Programades'
                usuari_notificacions.save()
            msg = Missatge( 
                        remitent= usuari_notificacions, 
                        text_missatge = u"Error enviant notificacions relació famílies.")    
            msg.afegeix_errors( errors.sort() )
            importancia = 'VI' 
            
            grupDireccio =  Group.objects.get( name = 'direcció' )
            msg.envia_a_grup( grupDireccio , importancia=importancia)
            
            