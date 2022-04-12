# -*- coding: utf-8 -*- 

import random
from demo.helpers import nomsICognoms
from datetime import timedelta, date
from django.template.defaultfilters import slugify
import csv
from aula.utils.tools import unicode
from os.path import exists

def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

def getRandomNomICognoms():
    return random.choice( nomsICognoms.noms ).capitalize(),  u"{c1} {c2}".format( c1 = random.choice( nomsICognoms.cognoms ).capitalize() , c2 = random.choice( nomsICognoms.cognoms ).capitalize() )


def getRandomRalc():
    return random.randint(10000000000,99999999999)

def generaFitxerSaga( path, nivellsCursosGrups, override ):

    # Format:
    # 1,"Aasss, ssss","09/03/1995","ssss , dfdfdfd","","","","","","","","CR Tarragona fdfd","Figueres","","+34-6543434343 (Primer telèfon de l)","17001218, Institut Ramon Muntaner, Figueres","CF adm 2"    

    fileexists = exists(path)
    if (not override and fileexists):
        return

    with open(path, 'w') as csvfile:
        spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

        spamwriter.writerow( ( "#","00_IDENTIFICADOR DE L'ALUMNE/A","01_NOM","02_DATA NAIXEMENT","03_RESPONSABLE 1","04_TELÈFON RESP. 1","05_MÒBIL RESP. 1","06_ADREÇA ELECTR. RESP. 1","07_RESPONSABLE 2","08_TELÈFON RESP. 2","09_MÒBIL RESP. 2","10_ADREÇA ELECTR. RESP. 2","11_ADREÇA","12_LOCALITAT","13_MUNICIPI","14_CORREU ELECTRÒNIC","15_ALTRES TELÈFONS","16_CENTRE PROCEDÈNCIA","17_GRUPSCLASSE", ) )
        for nivell, GrupsCursos in nivellsCursosGrups:
            for curs, Grups in GrupsCursos:
                for grup in Grups:
                    for _ in range( 10, random.randint( 20, 35 ) ):
                        ralc = getRandomRalc()
                        nom1, cognom1 = getRandomNomICognoms()
                        nom2, cognom2 = getRandomNomICognoms()
                        nom3, cognom3 = getRandomNomICognoms()
                        row = (
                                ##,
                                1,
                                # "00_IDENTIFICADOR DE L'ALUMNE/A",
                                u"{ralc}".format(ralc=ralc),
                                #"01_NOM",
                                u"{cognom}, {nom}".format( cognom=cognom1, nom=nom1 ),
                                #"02_DATA NAIXEMENT",
                                random_date( date( year=1990, month = 1, day = 1), date( year=2000, month = 1, day = 1)  ).strftime('%d/%m/%Y') ,
                                #"03_RESPONSABLE 1",
                                u"{cognom}, {nom}".format( cognom=cognom2, nom=nom2 ),
                                #"04_TELÈFON RESP. 1",
                                u"+34 XXXXXXX",
                                #"05_MÒBIL RESP. 1",
                                u"+34 XXXXXXX",
                                #"06_ADREÇA ELECTR. RESP. 1",
                                u"{correu}@mailintaor.com".format(correu=slugify(nom1)),
                                #"07_RESPONSABLE 2",
                                u"{cognom}, {nom}".format( cognom=cognom3, nom=nom3 ),
                                #"08_TELÈFON RESP. 2",
                                u"+34 XXXXZZZZ",
                                #"09_MÒBIL RESP. 2",
                                u"+34 XXXXLLL",
                                #"10_ADREÇA ELECTR. RESP. 2",
                                u"{correu}@mailintaor.com".format( correu = slugify( nom2 ) ),
                                #"11_ADREÇA",
                                u"c/ de l'aviador {nom} {cognom}".format( cognom=cognom3, nom=nom3  ),
                                #"12_LOCALITAT",
                                u"L'Armentera",  #TODO: llista de localitats
                                # "13_MUNICIPI",
                                u"Albanyà",  # TODO: llista de localitats
                                #"14_CORREU ELECTRÒNIC",
                                u"{correu}@mailintaor.com".format( correu = slugify( nom1 ) ),
                                #"15_ALTRES TELÈFONS",
                                u"+34 XXXXYZZY",
                                #"16_CENTRE PROCEDÈNCIA",
                                u"La Salle",
                                #"17_GRUPSCLASSE",
                                u"{nivell}{curs}{grup}".format( nivell = nivell, grup = grup, curs = curs)                           
                               )
                        #utfrow = [ unicode(s).encode("iso-8859-1") for s in row ]
                        spamwriter.writerow( row )

                        
    
    
        