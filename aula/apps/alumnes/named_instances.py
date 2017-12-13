# This Python file uses the following encoding: utf-8
from django.apps import apps
from django.conf import settings


def Nivells_no_obligatoris():
    Nivell = apps.get_model( 'alumnes','Nivell')
    return Nivell.objects.exclude( nom_nivell = 'ESO' )

def Nivells_obligatoris():
    Nivell = apps.get_model( 'alumnes','Nivell')
    return Nivell.objects.filter( nom_nivell = 'ESO' )

def Cursa_nivell(nivell_txt, alumne):
    return alumne.grup.curs.nivell.nom_nivell in settings.CUSTOM_NIVELLS[nivell_txt]

def curs_any_fi():
    Curs = apps.get_model( 'alumnes','Curs')
    return Curs.objects.filter( data_inici_curs__isnull = False )[0].data_inici_curs.year


