# This Python file uses the following encoding: utf-8

from django.core.management.base import BaseCommand, CommandError
#from incidencies.models import Incidencia, Expulsio
#dates
from datetime import date, timedelta

from django.db.models.loading import get_model


class Command(BaseCommand):
    help = 'Caduca les incidències i expulsions velles'    

    def handle(self, *args, **options):
        fa_30_dies = date.today() - timedelta( days = 30 )
        fa_60_dies = date.today() - timedelta( days = 60 )
        
        Incidencia = get_model( 'incidencies', 'Incidencia')
        Expulsio = get_model( 'incidencies', 'Expulsio')
        
        Incidencia.objects.filter( es_vigent = True, 
                                   dia_incidencia__lt = fa_30_dies).update( es_vigent = False )
        
        Expulsio.objects.filter( es_vigent = True,
                                 dia_expulsio__lt = fa_60_dies ).update( es_vigent = False )        
        self.stdout.write(u"Tasca finalitzada satisfactoriament")