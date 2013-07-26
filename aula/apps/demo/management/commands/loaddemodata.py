# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from aula.apps.demo.helpers.carrega import fesCarrega

class Command(BaseCommand):
    args = 'None'
    help = 'Carrega dades de prova'

    def handle(self, *args, **options):
        fesCarrega()
        self.stdout.write(u"Dades creades correctament")