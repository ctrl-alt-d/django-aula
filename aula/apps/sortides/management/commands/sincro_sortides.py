# This Python file uses the following encoding: utf-8

from django.core.management.base import BaseCommand

from aula.apps.missatgeria.missatges_a_usuaris import (
    ERROR_SINCRONITZANT_SORTIDES,
    tipusMissatge,
)
from aula.apps.sortides.sincronitza import sincronitza
from aula.utils.tools import unicode


class Command(BaseCommand):
    help = "Notifica a les families"

    def handle(self, *args, **options):
        try:
            self.stdout.write("Iniciant procés sincronitzacio sortides")
            sincronitza()
            self.stdout.write("Fi procés sincronitzacio sortides")
        except Exception as e:
            self.stdout.write(
                "Error al procés sincronitzacio sortides: {0}".format(unicode(e))
            )
            errors = [unicode(e)]

            # Deixar missatge a la base de dades (utilitzar self.user )
            from django.contrib.auth.models import Group, User

            from aula.apps.missatgeria.models import Missatge

            usuari_notificacions, new = User.objects.get_or_create(username="TP")
            if new:
                usuari_notificacions.is_active = False
                usuari_notificacions.first_name = "Usuari Tasques Programades"
                usuari_notificacions.save()
            missatge = ERROR_SINCRONITZANT_SORTIDES
            tipus_de_missatge = tipusMissatge(missatge)
            msg = Missatge(
                remitent=usuari_notificacions,
                text_missatge=missatge,
                tipus_de_missatge=tipus_de_missatge,
            )
            importancia = "VI"

            administradors, _ = Group.objects.get_or_create(name="administradors")

            msg.envia_a_grup(administradors, importancia=importancia)
            msg.afegeix_errors(errors)
