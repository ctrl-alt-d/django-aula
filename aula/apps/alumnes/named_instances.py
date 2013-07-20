# This Python file uses the following encoding: utf-8
from django.db.models.loading import get_model


def Nivells_no_obligatoris():
    Nivell = get_model( 'alumnes','Nivell')
    return Nivell.objects.exclude( nom_nivell = 'ESO' )

def Nivells_obligatoris():
    Nivell = get_model( 'alumnes','Nivell')
    return Nivell.objects.filter( nom_nivell = 'ESO' )

def curs_any_fi():
    Curs = get_model( 'alumnes','Curs')
    return Curs.objects.filter( data_inici_curs__isnull = False )[0].data_inici_curs.year


