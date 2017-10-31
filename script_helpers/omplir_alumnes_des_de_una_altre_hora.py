from datetime import datetime
from datetime import timedelta
from aula.apps.presencia.afegeixTreuAlumnesLlista import afegeixThread

dates = [
   datetime(2017,10,30),
   datetime(2017,10,31),
   datetime(2017,11,8),
   datetime(2017,11,2),
   datetime(2017,11,3),
]

una_setmana = timedelta( days = 14 )

from aula.apps.presencia.models import Impartir


from aula.apps.usuaris.models import Professor
dani_herrera = Professor.objects.get( username = 'INDH' )

debuga = False

for data in dates:
    for imparticio in Impartir.objects.filter( dia_impartir = data) : #, horari__professor = dani_herrera ):
        impartir_anteriors = Impartir.objects.filter( horari__hora = imparticio.horari.hora,
                                                  horari__assignatura = imparticio.horari.assignatura,
                                                  horari__professor = imparticio.horari.professor,
                                                  horari__grup = imparticio.horari.grup,
                                                  dia_impartir = data - una_setmana )
        if impartir_anteriors.count()   != 1:
            continue
        impartir_anterior=impartir_anteriors.get()
        alumnes = [ ca.alumne for ca in impartir_anterior.controlassistencia_set.all()]
        user = imparticio.horari.professor.getUser()
        if debuga:
            print ('Impartir ', impartir_anterior )
        else:
            afegeix=afegeixThread(expandir = False, alumnes=alumnes, impartir=imparticio, usuari = user, matmulla = False)
            afegeix.start()
            afegeix.join()

#
# from datetime import datetime
# from datetime import timedelta
# from aula.apps.presencia.afegeixTreuAlumnesLlista import afegeixThread
#
# dates = [
#    datetime(2015,5,5),
#    datetime(2015,5,6),
#    datetime(2015,5,7),
#    datetime(2015,5,8),
#    datetime(2015,5,11),
# ]
#
# una_setmana = timedelta( days = 14 )
#
# from aula.apps.presencia.models import Impartir
#
#
# from aula.apps.usuaris.models import Professor
# dani_herrera = Professor.objects.get( username = 'INDH' )
#
# debuga = False
#
# for data in dates:
#     for imparticio in Impartir.objects.filter( dia_impartir = data) : #, horari__professor = dani_herrera ):
#         impartir_anterior = Impartir.objects.get( horari = imparticio.horari,
#                                                   dia_impartir = data - una_setmana )
#         alumnes = [ ca.alumne for ca in impartir_anterior.controlassistencia_set.all()]
#         user = imparticio.horari.professor.getUser()
#         if debuga:
#             print ('Impartir ', imparticio,
#                   '\n Anterior ', impartir_anterior,
#                   '\n alumnes ', u', '.join( [str(x) for x in alumnes_pk] ) )
#         else:
#             afegeix=afegeixThread(expandir = False, alumnes=alumnes, impartir=imparticio, usuari = user, matmulla = False)
#             afegeix.start()
#             afegeix.join()
#
#
#
#
#
#
#
#
#
#
#
#