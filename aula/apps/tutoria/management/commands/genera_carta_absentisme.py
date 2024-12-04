from aula.apps.tutoria.avis_tutor_faltes import avisTutorCartaPerFaltes
from aula.utils.tools import unicode
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
  help = "Avisa a tutors de generació cartes d'absentisme"

  def handle(self, *args, **options):
      try:
          self.stdout.write(u"Iniciant procés avís tutors/es carta per faltes d'assitència")
          avisTutorCartaPerFaltes()
          self.stdout.write(u"Fi procés avís tutors/es carta per faltes d'assitència")
      except Exception as e:
          self.stdout.write(u"Error al procés d'avís: {0}".format(unicode(e)))
          errors = [unicode(e)]
