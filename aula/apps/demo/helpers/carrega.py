# -*- coding: utf-8 -*-
import os
from aula.apps.demo.helpers.alumnes import generaFitxerSaga
from aula.apps.demo.helpers.horaris import generaFitxerKronowin

from aula.apps.extKronowin import sincronitzaKronowin 
from aula.apps.extSaga import sincronitzaSaga

from datetime import date
from dateutil.relativedelta import relativedelta
from aula.apps.extKronowin.models import  Franja2Aula
from aula.apps.extSaga.models import Grup2Aula as SGrup2Aula
from aula.apps.alumnes.models import Grup

from django.contrib.auth.models import User, Group
from aula.apps.tutoria.models import Tutor
import random
from aula.apps.usuaris.models import Professor
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.presencia.regeneraImpartir import regeneraThread

def fesCarrega( ):
    msg = u""
    #Calen fixtures carregades:
    #      extKronowin incidencies presencia assignatures horaris seguimentTutorial missatgeria usuaris    
    
    fitxerSaga = os.path.join( os.path.dirname(__file__), '../tmp/exportSaga.txt')
    fitxerKronowin = os.path.join( os.path.dirname(__file__), '../tmp/exportKrono.txt')
    frangesMatins, frangesTardes = range(1,5), range(6,10) 
    userDemo, new = User.objects.get_or_create( username = 'demo', defaults={'is_staff':True, 'is_superuser':True, } )
    if new:
        userDemo.set_password( '1234' )
    
    nivellsCursosGrups = ( 
                            ( 'ESO', 
                              (
                                 ( 1, ( 'A','B','C'), ),
                                 ( 2, ( 'A','B',), ),
                                 ( 3, ( 'A','B',), ),
                              ),
                            ),
                            ( 'INF',
                              (
                                  ( 1, ( 'A',), ),
                                  ( 2, ( 'A',), ),
                              ),
                            ),
                            ( 'ADM',
                              (
                                  ( 1, ( 'A','B'), ),
                                  ( 2, ( 'A',), ),
                              ),
                            ),
                         )

    print u"#GENEREM FITXERS DE DADES  "                        
    generaFitxerSaga(fitxerSaga, nivellsCursosGrups  )
    generaFitxerKronowin( fitxerKronowin, nivellsCursosGrups, nivellsMatins=['ESO',], frangesMatins = frangesMatins, frangesTardes  = frangesTardes )
    
    print u"#CREEM NIVELL-CURS-GRUP"
    handlerKronowin=open( fitxerKronowin, 'r' )
    inici_curs = date.today()
    fi_curs = date.today() + relativedelta( months = 1)
    sincronitzaKronowin.creaNivellCursGrupDesDeKronowin( handlerKronowin, inici_curs, fi_curs )
    
    print u"#Creem correspondències amb horaris"
    frangesAula = FranjaHoraria.objects.filter( hora_inici__in = ['09:15', '10:30', '11:30' ,'12:45',
                                                                  '15:45', '16:45', '18:05', '19:00'] ).order_by ( 'hora_inici' )
    frangesKronowin = frangesMatins + frangesTardes
    for frangaAula, franjaKronowin in zip(frangesAula, frangesKronowin  ):
        Franja2Aula.objects.get_or_create( franja_kronowin= franjaKronowin,  franja_aula = frangaAula )
        
    print u"#CREEM CORRESPONDÈNCIES  SAGA-KRONOWIN-AULA"
    for nivell, GrupsCursos in nivellsCursosGrups:
        for curs, Grups in GrupsCursos:
            for grup in Grups:
                lgrup = u"{nivell}{curs}{grup}".format( nivell = nivell, grup = grup, curs = curs) 
                grupAula = Grup.objects.get( descripcio_grup = lgrup )
                SGrup2Aula.objects.create( grup_saga = lgrup, Grup2Aula = grupAula  )
                #KGrup2Aula.objects.create( grup_kronowin = lgrup, Grup2Aula = grupAula  )   #ho fa als crear els grups

    print u"#Importem Kronowin 1 ( Per crear professors )"
    handlerKronowin=open( fitxerKronowin, 'r' )
    sincronitzaKronowin.sincronitza( handlerKronowin, userDemo  )
    
    print u"#Importem Kronowin 2 ( Per importar horaris )"
    handlerKronowin=open( fitxerKronowin, 'r' )
    sincronitzaKronowin.sincronitza( handlerKronowin, userDemo  )

    print u"#Importem saga"
    handlerSaga=open( fitxerSaga, 'r' )
    sincronitzaSaga.sincronitza( handlerSaga, userDemo  )
    
    print u"#Assignem tutors"
    for g in Grup.objects.all():
        professors_del_grup = Professor.objects.filter( horari__grup = g ).distinct()
        if professors_del_grup:
            Tutor.objects.create( professor = random.choice( professors_del_grup ) ,  grup = g )
    
    msg += "\nTutors: " + u" ,".join( set( [ unicode( t.professor.username ) for t in Tutor.objects.all() ] ) )
                    
    print u"#Assignem equip directiu"
    direccio, _ = Group.objects.get_or_create(name= 'direcció' )
    sisplau_que_no_siguin_mediocres = [ random.choice(  Professor.objects.all() ) ] + [ p for p in Professor.objects.filter( username__endswith = '1' )]
    for sisplau_que_no_sigui_mediocre in sisplau_que_no_siguin_mediocres:
        sisplau_que_no_sigui_mediocre.groups.add( direccio  )
        sisplau_que_no_sigui_mediocre.is_staff = True
        sisplau_que_no_sigui_mediocre.is_superuser = True
        sisplau_que_no_sigui_mediocre.save()    
    msg += u"\nDirecció: "  + u" ,".join( set( [ unicode( t.username ) for t.username in sisplau_que_no_siguin_mediocres ]  ) )
    
    print u"Regenerar impartir"
    r=regeneraThread(
                    data_inici= inici_curs, 
                    franja_inici = FranjaHoraria.objects.all()[:1].get(),
                    user = userDemo
                    )
    r.start()    
    r.join()
    
    return msg


    
    
    
    
    