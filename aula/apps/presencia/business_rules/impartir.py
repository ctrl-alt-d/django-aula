# This Python file uses the following encoding: utf-8
from django.apps import apps

#-------------Impartir-------------------------------------------------------------
from aula.apps.aules.models import ReservaAula, Aula
from aula.apps.horaris.models import FranjaHoraria


def impartir_clean( instance ):
    pass

def impartir_pre_delete( sender, instance, **kwargs):
    pass
    
def impartir_pre_save(sender, instance,  **kwargs):

    #bussiness rule: una impartició afegirà una reserva d'aula

    #Determinar quina és la franja horària mínima i màxima
    #del dia de la impartició
    franjes = FranjaHoraria.objects.all()
    franja_baixa = franjes.first()
    franja_alta = franjes.last()
    franjes_minimes = {'0': None, '1': None, '2': None, '3': None, '4': None, '5': None, '6': None, }
    franjes_maximes = {'0': None, '1': None, '2': None, '3': None, '4': None, '5': None, '6': None, }
    #imparticions = Impartir.objects.all()
    #for imparticio in imparticions:
    #    print imparticio.horari.dia_de_la_setmana, imparticio.horari.dia_de_la_setmana.n_dia_ca
    if instance.horari.dia_de_la_setmana.n_dia_ca == 0:
            if franjes_minimes['0'] == None or instance.horari.hora.hora_inici < franjes_minimes['0']:
                franjes_minimes['0'] = instance.horari.hora.hora_inici
            if franjes_maximes['0'] == None or instance.horari.hora.hora_fi > franjes_maximes['0']:
                franjes_maximes['0'] = instance.horari.hora.hora_fi
    elif instance.horari.dia_de_la_setmana.n_dia_ca == 1:
            if franjes_minimes['1'] == None or instance.horari.hora.hora_inici < franjes_minimes['1']:
                franjes_minimes['1'] = instance.horari.hora.hora_inici
            if franjes_maximes['1'] == None or instance.horari.hora.hora_fi > franjes_maximes['1']:
                franjes_maximes['1'] = instance.horari.hora.hora_fi
    elif instance.horari.dia_de_la_setmana.n_dia_ca == 2:
            if franjes_minimes['2'] == None or instance.horari.hora.hora_inici < franjes_minimes['2']:
                franjes_minimes['2'] = instance.horari.hora.hora_inici
            if franjes_maximes['2'] == None or instance.horari.hora.hora_fi > franjes_maximes['2']:
                franjes_maximes['2'] = instance.horari.hora.hora_fi
    elif instance.horari.dia_de_la_setmana.n_dia_ca == 3:
            if franjes_minimes['3'] == None or instance.horari.hora.hora_inici < franjes_minimes['3']:
                franjes_minimes['3'] = instance.horari.hora.hora_inici
            if franjes_maximes['3'] == None or instance.horari.hora.hora_fi > franjes_maximes['3']:
                franjes_maximes['3'] = instance.horari.hora.hora_fi
    elif instance.horari.dia_de_la_setmana.n_dia_ca == 4:
            if franjes_minimes['4'] == None or instance.horari.hora.hora_inici < franjes_minimes['4']:
                franjes_minimes['4'] = instance.horari.hora.hora_inici
            if franjes_maximes['4'] == None or instance.horari.hora.hora_fi > franjes_maximes['4']:
                franjes_maximes['4'] = instance.horari.hora.hora_fi
    elif instance.horari.dia_de_la_setmana.n_dia_ca == 5:
            if franjes_minimes['5'] == None or instance.horari.hora.hora_inici < franjes_minimes['5']:
                franjes_minimes['5'] = instance.horari.hora.hora_inici
            if franjes_maximes['5'] == None or instance.horari.hora.hora_fi > franjes_maximes['5']:
                franjes_maximes['5'] = instance.horari.hora.hora_fi
    elif instance.horari.dia_de_la_setmana.n_dia_ca == 6:
            if franjes_minimes['6'] == None or instance.horari.hora.hora_inici < franjes_minimes['6']:
                franjes_minimes['6'] = instance.horari.hora.hora_inici
            if franjes_maximes['6'] == None or instance.horari.hora.hora_fi > franjes_maximes['6']:
                franjes_maximes['6'] = instance.horari.hora.hora_fi
    #Assignar disponibilitats per dia a partir de franjes mínima i màxima obtingudes
    disponibilitats = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [],6: []}  #ve donada per la franja mínima i màxima de cada dia de la setmana
    disponibilitats['0'] = FranjaHoraria.objects.filter(hora_inici__gte=franjes_minimes['0']).exclude(
        hora_fi__gt=franjes_maximes['0']) if franjes_minimes['0'] != None else None
    disponibilitats['1'] = FranjaHoraria.objects.filter(hora_inici__gte=franjes_minimes['1']).exclude(
        hora_fi__gt=franjes_maximes['1']) if franjes_minimes['1'] != None else None
    disponibilitats['2'] = FranjaHoraria.objects.filter(hora_inici__gte=franjes_minimes['2']).exclude(
        hora_fi__gt=franjes_maximes['2']) if franjes_minimes['2'] != None else None
    disponibilitats['3'] = FranjaHoraria.objects.filter(hora_inici__gte=franjes_minimes['3']).exclude(
        hora_fi__gt=franjes_maximes['3']) if franjes_minimes['3'] != None else None
    disponibilitats['4'] = FranjaHoraria.objects.filter(hora_inici__gte=franjes_minimes['4']).exclude(
        hora_fi__gt=franjes_maximes['4']) if franjes_minimes['4'] != None else None
    disponibilitats['5'] = FranjaHoraria.objects.filter(hora_inici__gte=franjes_minimes['5']).exclude(
        hora_fi__gt=franjes_maximes['5']) if franjes_minimes['5'] != None else None
    disponibilitats['6'] = FranjaHoraria.objects.filter(hora_inici__gte=franjes_minimes['6']).exclude(
        hora_fi__gt=franjes_maximes['6']) if franjes_minimes['6'] != None else None
    #print "Creada disponibilitat per dies de la setmana"
    noms_aules = []
    #for imparticio in imparticions:
    #si la impartició té assignada nom d'aula es crea la reserva
    if instance.horari.aula.nom_aula:
            nomaula = instance.horari.aula.nom_aula
            # if nomaula not in noms_aules:
            #     disponibilitat = disponibilitats[imparticio.horari.dia_de_la_setmana.n_dia_ca]
            #
            #     novaaula = Aula(nom_aula=nomaula,
            #                     descripcio_aula="Aula : " + nomaula,
            #                     horari_lliure=False,
            #                     reservable=True)
            #     novaaula.save()
            #     novaaula.disponibilitat_horaria = disponibilitat
            #     novaaula.save()
            #     noms_aules.append(nomaula)
            #     print 'Aula creada'
            #else:
            #print 'Aula ja existeix, afegeix reserva'
            aula = Aula.objects.get(nom_aula=nomaula)
            #    print novaaula.nom_aula, imparticio.dia_impartir, imparticio.horari.hora.hora_inici
            novareserva = ReservaAula(aula=aula,
                                      dia_reserva=instance.dia_impartir,
                                      hora_inici=instance.horari.hora.hora_inici,
                                      hora_fi=instance.horari.hora.hora_fi,
                                      hora=instance.horari.hora,
                                      usuari=instance.horari.professor,
                                      motiu="Docencia habitual")
            novareserva.save()

    instance.clean()





def impartir_post_save(sender, instance, created, **kwargs):
    #bussiness rule:
    #si un professor passa llista, també passa llista de 
    #totes les imparticions que no tinguin alumnes.
    if instance.professor_passa_llista is not None:
        Impartir = apps.get_model('presencia','Impartir')
        altresHores = Impartir.objects.filter( horari__hora = instance.horari.hora, 
                                               dia_impartir = instance.dia_impartir,
                                               controlassistencia__isnull = True,
                                               horari__professor = instance.horari.professor,
                                               horari__grup__isnull = False  )
        
        altresHores.update( professor_passa_llista = instance.professor_passa_llista,
                           dia_passa_llista = instance.dia_passa_llista )
    
    pass

def impartir_despres_de_passar_llista(instance):
    #Si passa llista un professor que no és el de l'Horari cal avisar.
    if instance.professor_passa_llista <> instance.horari.professor:
        remitent = instance.professor_passa_llista
        text_missatge = u"""Has passat llista a un grup que no és el teu: ({0}). 
                         El professor del grup {1} rebrà un missatge com aquest.
                         """.format( unicode(instance),  unicode(instance.horari.professor) )
        Missatge = apps.get_model( 'missatgeria','Missatge')
        msg = Missatge( remitent = remitent.getUser(), text_missatge = text_missatge )           
        msg.envia_a_usuari( usuari = instance.professor_passa_llista.getUser(), importancia = 'VI')

        text_missatge = u"""Ha passat llista d'una classe on consta que la fas tú: ({0}). 
                         """.format( unicode(instance),  unicode(instance.horari.professor) )
        msg = Missatge( remitent = remitent.getUser(), text_missatge = text_missatge )           
        msg.envia_a_usuari( usuari = instance.horari.professor.getUser(), importancia = 'VI')
    

