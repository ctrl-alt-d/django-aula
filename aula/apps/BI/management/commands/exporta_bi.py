# This Python file uses the following encoding: utf-8

from django.core.management.base import BaseCommand, CommandError
from aula.apps.BI.utils import fact_controls

class Command(BaseCommand):
    help = 'Exporta fitxer de BI'

    def handle(self, *args, **options):
        fact_controls()
        self.stdout.write(u"Fitxer exportat correctament")