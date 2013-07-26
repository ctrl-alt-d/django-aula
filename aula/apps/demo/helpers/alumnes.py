# -*- coding: utf-8 -*- 

import random
from aula.apps.demo.helpers import nomsICognoms
from datetime import timedelta, date
from django.template.defaultfilters import slugify
import csv

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
    return random.choice( nomsICognoms.noms ),  u"{c1} {c2}".format( c1 = random.choice( nomsICognoms.cognoms ) , c2 = random.choice( nomsICognoms.cognoms ) )
    
def generaFitxerSaga( path, nivellsCursosGrups ):


#1,"Aasss, ssss","09/03/1995","ssss , dfdfdfd","","","","","","","","CR Tarragona fdfd","Figueres","","+34-6543434395 (Primer telèfon de l)","17001218, Institut Ramon Muntaner, Figueres","CF adm 2"    

    with open(path, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

        spamwriter.writerow( ( "#","00_NOM","01_DATA NAIXEMENT","02_RESPONSABLE 1","03_TELÈFON RESP. 1","04_MÒBIL RESP. 1","05_ADREÇA ELECTR. RESP. 1","06_RESPONSABLE 2","07_TELÈFON RESP. 2","08_MÒBIL RESP. 2","09_ADREÇA ELECTR. RESP. 2","10_ADREÇA","11_LOCALITAT","12_CORREU ELECTRÒNIC","13_ALTRES TELÈFONS","14_CENTRE PROCEDÈNCIA","15_GRUPSCLASSE", ) ) 
        for nivell, GrupsCursos in nivellsCursosGrups:
            for curs, Grups in GrupsCursos:
                for grup in Grups:
                    for _ in range( 10, random.randint( 20, 35 ) ):
                        nom1, cognom1 = getRandomNomICognoms()
                        nom2, cognom2 = getRandomNomICognoms()
                        nom3, cognom3 = getRandomNomICognoms()
                        row = (
                                ##,
                                1,
                                #"00_NOM",
                                u"{cognom}, {nom}".format( cognom=cognom1, nom=nom1 ),
                                #"01_DATA NAIXEMENT",
                                random_date( date( year=1990, month = 1, day = 1), date( year=2000, month = 1, day = 1)  ).strftime('%d/%m/%Y') ,                            
                                #"02_RESPONSABLE 1",
                                u"{cognom}, {nom}".format( cognom=cognom2, nom=nom2 ),
                                #"03_TELÈFON RESP. 1",
                                u"+34 XXXXXXX",
                                #"04_MÒBIL RESP. 1",
                                u"+34 XXXXXXX",
                                #"05_ADREÇA ELECTR. RESP. 1",                            
                                u"c/ del General {nom} {cognom}".format( cognom=cognom3, nom=nom3  ),                            
                                #"06_RESPONSABLE 2",
                                u"+34 XXXXXYYY",
                                #"07_TELÈFON RESP. 2",
                                u"+34 XXXXZZZZ",
                                #"08_MÒBIL RESP. 2",
                                u"+34 XXXXLLL",
                                #"09_ADREÇA ELECTR. RESP. 2",
                                u"{correu}@mailintaor.com".format( correu = slugify( nom2 ) ),
                                #"10_ADREÇA",
                                u"c/ de l'aviador {nom} {cognom}".format( cognom=cognom3, nom=nom3  ),                            
                                #"11_LOCALITAT",
                                u"L'Armentera",    #TODO: llista de localitats
                                #"12_CORREU ELECTRÒNIC",
                                u"{correu}@mailintaor.com".format( correu = slugify( nom1 ) ),
                                #"13_ALTRES TELÈFONS",
                                u"",
                                #"14_CENTRE PROCEDÈNCIA",
                                u"La Salle",
                                #"15_GRUPSCLASSE",
                                u"{nivell}{curs}{grup}".format( nivell = nivell, grup = grup, curs = curs)                           
                               )
                        utfrow = [ unicode(s).encode("iso-8859-1") for s in row ]
                        spamwriter.writerow( utfrow )

                        
    
    
        
