from django.core.management.base import BaseCommand

from aula.apps.tutoria.avis_tutor_faltes import avisTutorCartaPerFaltes
from aula.utils.tools import unicode


class Command(BaseCommand):
    help = "Avisa a tutors de generació cartes d'absentisme"

    def handle(self, *args, **options):
        try:
            self.stdout.write(
                "Iniciant procés avís tutors/es carta per faltes d'assitència"
            )
            avisTutorCartaPerFaltes()
            self.stdout.write("Fi procés avís tutors/es carta per faltes d'assitència")
        except Exception as e:
            self.stdout.write("Error al procés d'avís: {0}".format(unicode(e)))
            [unicode(e)]
