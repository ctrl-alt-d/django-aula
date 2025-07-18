# This Python file uses the following encoding: utf-8

from aula.apps.horaris.abstract_models import (
    AbstractDiaDeLaSetmana,
    AbstractFestiu,
    AbstractFranjaHoraria,
    AbstractHorari,
)


class DiaDeLaSetmana(AbstractDiaDeLaSetmana):
    pass


class FranjaHoraria(AbstractFranjaHoraria):
    pass


class Horari(AbstractHorari):
    pass


class Festiu(AbstractFestiu):
    pass
