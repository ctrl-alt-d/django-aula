# -*- coding: utf-8 -*-
import os
from demo.helpers.alumnes import generaFitxerSaga, getRandomNomICognoms
from demo.helpers.horaris import generaFitxerKronowin

from aula.apps.extKronowin import sincronitzaKronowin 
from aula.apps.extSaga import sincronitzaSaga

from datetime import date
from dateutil.relativedelta import relativedelta
from aula.apps.extKronowin.models import  Franja2Aula
from aula.apps.extSaga.models import Grup2Aula as SGrup2Aula
from aula.apps.alumnes.models import Grup, Alumne

from django.contrib.auth.models import User, Group
from aula.apps.tutoria.models import Tutor
import random
from aula.apps.usuaris.models import Professor
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.alumnes.gestioGrups import grupsPotencials
from aula.apps.presencia.regeneraImpartir import regeneraThread
from aula.apps.presencia.models import Impartir, EstatControlAssistencia

from aula.apps.presencia.afegeixTreuAlumnesLlista import afegeixThread
from aula.utils.tools import unicode

def fesCarrega( ):
    msg = u""
    #Calen fixtures carregades:
    #      extKronowin incidencies presencia assignatures horaris seguimentTutorial missatgeria usuaris    
    
    fitxerSaga = os.path.join( os.path.dirname(__file__), '../tmp/exportSaga.txt')
    fitxerKronowin = os.path.join( os.path.dirname(__file__), '../tmp/exportKrono.txt')
    frangesMatins, frangesTardes = range(1,5), range(6,10) 
    userDemo, new = User.objects.get_or_create( username = 'demo', defaults={'is_staff':True, 'is_superuser':True, } )
    if new:
        userDemo.set_password( 'djAu' )
    
    nivellsCursosGrups = ( 
                            ( 'ESO', 
                              (
                                 ( 1, ( 'A','B','C'), ),
                                 ( 2, ( 'A','B',), ),
                                 ( 3, ( 'A','B',), ),
                              ),
                            ),
                            ( 'CFI',
                              (
                                  ( 1, ( 'A',), ),
                                  ( 2, ( 'A',), ),
                              ),
                            ),
                            ( 'CFA',
                              (
                                  ( 1, ( 'A','B'), ),
                                  ( 2, ( 'A',), ),
                              ),
                            ),
                         )

    print (u"#GENEREM FITXERS DE DADES  ")                        
    generaFitxerSaga(fitxerSaga, nivellsCursosGrups, override=False  )
    generaFitxerKronowin( fitxerKronowin, nivellsCursosGrups, nivellsMatins=['ESO',], frangesMatins = frangesMatins, frangesTardes  = frangesTardes, override=False )
    
    print (u"#CREEM NIVELL-CURS-GRUP")
    handlerKronowin=open( fitxerKronowin, 'r' )
    inici_curs = date.today() + relativedelta( months = -1)
    fi_curs = date.today() + relativedelta( days = 10 )
    sincronitzaKronowin.creaNivellCursGrupDesDeKronowin( handlerKronowin, inici_curs, fi_curs )
    
    print (u"#Creem correspondències amb horaris")
    frangesAula = FranjaHoraria.objects.filter( hora_inici__in = ['09:15', '10:30', '11:30' ,'12:45',
                                                                  '15:45', '16:45', '18:05', '19:00'] ).order_by ( 'hora_inici' )
    frangesKronowin = list(frangesMatins) + list(frangesTardes)
    for frangaAula, franjaKronowin in zip(frangesAula, frangesKronowin  ):
        Franja2Aula.objects.get_or_create( franja_kronowin= franjaKronowin,  franja_aula = frangaAula )
        
    print (u"#CREEM CORRESPONDÈNCIES  SAGA-KRONOWIN-AULA")
    for nivell, GrupsCursos in nivellsCursosGrups:
        for curs, Grups in GrupsCursos:
            for grup in Grups:
                lgrup = u"{nivell}{curs}{grup}".format( nivell = nivell, grup = grup, curs = curs) 
                grupAula = Grup.objects.get( descripcio_grup = lgrup )
                SGrup2Aula.objects.create( grup_saga = lgrup, Grup2Aula = grupAula  )
                #KGrup2Aula.objects.create( grup_kronowin = lgrup, Grup2Aula = grupAula  )   #ho fa als crear els grups

    print (u"#Importem Kronowin 1 ( Per crear professors )")
    handlerKronowin=open( fitxerKronowin, 'r' )
    result = sincronitzaKronowin.sincronitza( handlerKronowin, userDemo  )
    print (u"Resultat importació kroniwin 1: ", result["errors"], result["warnings"], sep=" ")  
    
    print (u"#Importem Kronowin 2 ( Per importar horaris )")
    handlerKronowin=open( fitxerKronowin, 'r' )
    result = sincronitzaKronowin.sincronitza( handlerKronowin, userDemo  )
    print (u"Resultat importació kroniwin 2: ", result["errors"], result["warnings"], sep=" ")  

    print (u"#Importem saga")
    handlerSaga=open( fitxerSaga, 'r' )
    result = sincronitzaSaga.sincronitza( handlerSaga, userDemo  )
    print (u"Resultat importació saga: ", result["errors"], result["warnings"], sep=" ")  
    
    print (u"#Assignem tutors")
    for g in Grup.objects.all():
        professors_del_grup = Professor.objects.filter( horari__grup = g ).distinct()
        if professors_del_grup:
            Tutor.objects.create( professor = random.choice( professors_del_grup ) ,  grup = g )
    
    msg += "\nProfessors: " + u" ,".join( sorted( set( [ unicode( t.username ) for t in Professor.objects.all() ] ) ) )
    msg += "\nTutors: " + u" ,".join( sorted( set( [ unicode( t.professor.username ) for t in Tutor.objects.all() ] ) ) )
                    
    print (u"#Assignem equip directiu")
    direccio, _ = Group.objects.get_or_create(name= 'direcció' )
    sisplau_que_no_siguin_mediocres = [ random.choice(  Professor.objects.all() ) ] + [ p for p in Professor.objects.filter( username__endswith = '1' )]
    for sisplau_que_no_sigui_mediocre in sisplau_que_no_siguin_mediocres:
        sisplau_que_no_sigui_mediocre.groups.add( direccio  )
        sisplau_que_no_sigui_mediocre.is_staff = True
        sisplau_que_no_sigui_mediocre.is_superuser = True
        sisplau_que_no_sigui_mediocre.save()    
    msg += u"\nDirecció: "  + u" ,".join( sorted( set( [ unicode( t.username ) for t in sisplau_que_no_siguin_mediocres ]  ) ) )
    
    print (u"Regenerar impartir")
    r=regeneraThread(
                    data_inici= None,       #data inici de curs 
                    franja_inici = FranjaHoraria.objects.all()[:1].get(),
                    user = userDemo
                    )
    r.start()    
    r.join()
    
    print (u"Posar alumnes a llistes")
    seguents7dies = Impartir.objects.values( 'dia_impartir').order_by('dia_impartir').distinct()[:5]
    for dia in seguents7dies:
        print ('Dia', dia, u' ( ompliré 5 dies )', sep=" ")
        for impartir in Impartir.objects.filter( dia_impartir = dia['dia_impartir'] ):
            if not impartir.controlassistencia_set.exists():
                alumnes =  [ alumne for grup in grupsPotencials(impartir.horari) for alumne in grup.alumne_set.all() ] 
                random.shuffle( alumnes )
                n_alumnes = random.randint( 1,4 )
                afegeix=afegeixThread(expandir = False, alumnes=alumnes[:n_alumnes], impartir=impartir, usuari = impartir.horari.professor, matmulla = False)
                afegeix.start()
                afegeix.join()
    
    print ("posem unes quantes faltes d'assistència")
    alumnes_faltons = random.sample( list(Alumne.objects.all()), 20 )
    falta = EstatControlAssistencia.objects.get( codi_estat = "F" )
    for alumne_falton in alumnes_faltons:
        for ca in alumne_falton.controlassistencia_set.filter( impartir__dia_impartir__lt = date.today() ):
            ca.estat = falta
            ca.professor = ca.impartir.horari.professor
            ca.save()
            ca.impartir.professor_passa_llista = ca.impartir.horari.professor
            ca.impartir.dia_passa_llista = date.today()
            ca.impartir.save()


    print (u"canviant dades dels professors")
    for p in Professor.objects.all():
        p.first_name, p.last_name = getRandomNomICognoms() 
        p.set_password( 'djAu' )
        p.save()
        
    msg += u"\nTots els passwords de professors: 'djAu' "
        
    return msg

