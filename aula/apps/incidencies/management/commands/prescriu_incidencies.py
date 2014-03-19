# This Python file uses the following encoding: utf-8

from django.core.management.base import BaseCommand, CommandError
from aula.apps.incidencies.helpers import preescriu

class Command(BaseCommand):
    help = 'Caduca les incidències i expulsions velles'
    
    preescriu()    

    def handle(self, *args, **options):
        self.stdout.write(u"Tasca finalitzada satisfactoriament")
        
