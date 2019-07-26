# This Python file uses the following encoding: utf-8

# --
from django.contrib.auth.models import Group

from aula.apps.missatgeria.missatges_a_usuaris import RECORDA_REPROGRAMAR_CLASSES, tipusMissatge
from aula.apps.usuaris.models import Professor

from aula.apps.horaris.models import Horari, DiaDeLaSetmana
from aula.apps.extKronowin.models import Franja2Aula, Grup2Aula, ParametreKronowin
from aula.apps.assignatures.models import Assignatura
from aula.apps.aules.models import Aula
import traceback

import csv
from aula.apps.alumnes.models import Nivell, Grup, Curs

from aula.utils.tools import unicode

def sincronitza(file, usuari):
    _, _ = Group.objects.get_or_create(name=u'direcció')
    grupProfessors, _ = Group.objects.get_or_create(name='professors')
    grupProfessionals, _ = Group.objects.get_or_create(name='professional')
    grupConsergeria, _ = Group.objects.get_or_create(name='consergeria')

    dialect = csv.Sniffer().sniff(file.readline())
    file.seek(0)
    file.readline()
    file.seek(0)
    fieldnames = (
    'assignatura', 'professor', 'grup', 'mati_tarda', 'nivell', 'curs', 'lletra', 'aula', 'unk2', 'dia', 'franja',
    'unk3')
    reader = csv.DictReader(file, fieldnames=fieldnames, dialect=dialect)

    errors = []
    warnings = []
    infos = []

    # cal comprova número de columnes
    aFranges = set([])
    aGrups = set([])
    aProfessors = set([])

    #
    #
    #  PRIMERA PART: comprovar franjes horàries, grups i professors
    #
    #


    for row in reader:

        #
        # comprovar existència franges horàries Kronowin
        #
        codiFranja = unicode(row['franja'], 'iso-8859-1')
        aFranges.add(codiFranja)
        aTotesLesFrangesKronowin = set([])
        for f2g in Franja2Aula.objects.all(): aTotesLesFrangesKronowin.add(f2g.franja_kronowin)
        # les franges pendents:
        for f2g in aFranges.difference(aTotesLesFrangesKronowin):
            errors.append(u'Cal assignar la franja horària kronowin \'%s\' a una franja horària des d\'admin' % f2g)
            Franja2Aula(franja_kronowin=f2g).save()

        #
        # comprovar existència  grups Kronowin
        #
        codiGrup = unicode(row['grup'], 'iso-8859-1')
        aGrups.add(codiGrup)
        aTotsElsGrupsKronowin = set([])
        for g2g in Grup2Aula.objects.all(): aTotsElsGrupsKronowin.add(g2g.grup_kronowin)
        aTotsElsGrupsKronowin.add('')
        # els grups pendents:
        for g2g in aGrups.difference(aTotsElsGrupsKronowin):
            errors.append(u'Cal assignar el grup kronowin \'%s\' a un grup des d\'admin' % g2g)
            Grup2Aula(grup_kronowin=g2g).save()

        #
        # comprovar existència professors Kronowin
        #
        codiProfessor = unicode(row['professor'], 'iso-8859-1')
        aProfessors.add(codiProfessor)
        aTotsElsProfessors = set([])
        for p2g in Professor.objects.all(): aTotsElsProfessors.add(p2g.username)
        # els professors pendents:
        for p2g in aProfessors.difference(aTotsElsProfessors):
            parametre_passwd, _ = ParametreKronowin.objects.get_or_create(nom_parametre='passwd',
                                                                          defaults={'valor_parametre': '1234', })
            passwd = parametre_passwd.valor_parametre
            warnings.append(u'Nou usuari: \'%s\'. Passwd: \'%s\'' % (p2g, passwd))
            nouProfessor = Professor(username=p2g)
            nouProfessor.set_password(passwd)
            nouProfessor.save()
            nouProfessor.groups.add(grupProfessors)
            nouProfessor.groups.add(grupProfessionals)

            # Si detecto errors plego aquí:
    if errors: return {'errors': errors, 'warnings': warnings, 'infos': infos}

    #
    #
    #  SEGONA PART: importar
    #
    #
    nLiniesLlegides = 0
    nHorarisModificats = 0
    nAssignaturesCreades = 0
    nAulesCreades = 0
    file.seek(0)
    reader = csv.DictReader(file, fieldnames=fieldnames, dialect=dialect)
    Horari.objects.update(es_actiu=False)
    for row in reader:

        try:
            horari = Horari()
            # hora
            franja_kronowin = unicode(row['franja'], 'iso-8859-1')
            if franja_kronowin == '0,00':
                warnings.append('Horari no importat, Hora a 0,00: ' + unicode(row))
                continue
            horari.hora = Franja2Aula.objects.get(franja_kronowin=franja_kronowin).franja_aula

            # txt_curs
            # txt_curs =  unicode(row['curs'],'iso-8859-1')

            # nivell
            # txt_nivell =  unicode(row['nivell'],'iso-8859-1')

            # grup kronowin
            grup_kronowin = unicode(row['grup'], 'iso-8859-1')

            # grup
            curs = None
            if (grup_kronowin):
                horari.grup = Grup2Aula.objects.get(grup_kronowin=grup_kronowin).Grup2Aula
                curs = horari.grup.curs
                # professor
            codi_professor = unicode(row['professor'], 'iso-8859-1')
            horari.professor = Professor.objects.get(username=codi_professor)

            # assignatura
            # ---comprovo si cal afegir el codi professor al codi assignatura:
            codi_assignatura = unicode(row['assignatura'], 'iso-8859-1')
            assignatures_amb_professor, created = ParametreKronowin.objects.get_or_create(
                nom_parametre='assignatures amb professor')
            cal_afegir_profe = False
            assignatures_amb_professor_value_list = assignatures_amb_professor.valor_parametre.split(',')
            for prefixe_assignatura in [x.strip() for x in assignatures_amb_professor_value_list if bool( x.strip() )]:
                cal_afegir_profe = cal_afegir_profe or codi_assignatura.startswith(prefixe_assignatura.replace(' ', ''))
                # ---busco l'assignatura:
            codi_assignatura = codi_assignatura + '-' + codi_professor if cal_afegir_profe else codi_assignatura
            assignatura = None
            try:
                assignatura = Assignatura.objects.get(curs=curs, codi_assignatura=codi_assignatura)
            except Assignatura.DoesNotExist:  # cal crear l'assignatura
                nAssignaturesCreades += 1
                assignatura = Assignatura()
                assignatura.codi_assignatura = codi_assignatura
                assignatura.nom_assignatura = codi_assignatura
                # miro a quin curs pertany
                if (grup_kronowin):
                    assignatura.curs = Grup2Aula.objects.get(grup_kronowin=grup_kronowin).Grup2Aula.curs
                    # i save:
                assignatura.save()
            horari.assignatura = assignatura

            #aula
            nom_aula = unicode(row['aula'], 'iso-8859-1')
            if bool(nom_aula):
                aula, create = Aula.objects.get_or_create( nom_aula=nom_aula )
                nAulesCreades += 1 if created else 0
            else:
                aula = None
            
            horari.aula = aula

            # dia_de_la_setmana
            dia_kronowin = int(unicode(row['dia'], 'iso-8859-1').split(',')[0]) - 1
            horari.dia_de_la_setmana = DiaDeLaSetmana.objects.get(n_dia_ca=dia_kronowin)

            # estat_sincronitzacio
            horari.estat_sincronitzacio = '1'

            nouHorari, created = Horari.objects.get_or_create(
                hora=horari.hora,
                grup=horari.grup,
                professor=horari.professor,
                assignatura=horari.assignatura,
                dia_de_la_setmana=horari.dia_de_la_setmana,
                defaults={'es_actiu': True, })

            nouHorari.es_actiu = True
            nouHorari.aula = horari.aula
            nouHorari.save()

            if created:
                nHorarisModificats += 1

        except Exception as e:
            warnings.append('Horari no importat, [' + unicode(e) + '] :' + unicode(row))
            warnings.append( traceback.format_exc() )

        finally:
            nLiniesLlegides += 1

    # Solucionem problema de classes que es realitzen en més d'un grup.
    # Posar les entrades anteriors dels grups B, C, etc... inactives.
    # By Joan Rodríguez (INS Vidreres)
    fussionar_assignatures, _ = ParametreKronowin.objects.get_or_create(nom_parametre='fusionar assignatures',
                                                                        defaults={'valor_parametre': 'N', })
    if fussionar_assignatures.valor_parametre == 'S':
        horaris = ( Horari
                   .objects
                   .filter(es_actiu=True, grup__isnull=False)
                   .values_list('assignatura_id', 'professor_id',
                                'dia_de_la_setmana_id',
                                'hora_id')
                   .distinct() )

        for assignatura_id, professor_id, dia_de_la_setmana_id, hora_id in horaris:
            horaris_hora = ( Horari
                            .objects
                            .filter(es_actiu=True, 
                                    assignatura_id=assignatura_id,
                                    professor_id=professor_id, 
                                    dia_de_la_setmana_id=dia_de_la_setmana_id,
                                    hora_id=hora_id, 
                                    grup__isnull=False) )
            horari_primer_grup = horaris_hora.order_by('grup')[0]
            # per a debugar:
            # horari_altres_grups = horaris_hora.exclude( pk = horari_primer_grup.pk )
            # if horari_altres_grups:
            #	print horari_primer_grup.professor, horari_primer_grup.assignatura, horari_primer_grup.dia_de_la_setmana, horari_primer_grup.hora, ",",horari_primer_grup.grup,",",horari_altres_grups.values_list('grup__nom_grup')
            horaris_hora.exclude(pk=horari_primer_grup.pk).update(es_actiu=False)


    ambErrors = ' amb errors' if errors else ''
    ambAvisos = ' amb avisos' if not errors and warnings else ''

    infos.append(u'Importació finalitzada' + ambErrors + ambAvisos)
    infos.append(u' ')
    infos.append(u'%d línies llegides' % (nLiniesLlegides,))
    infos.append(u'%d horaris creats o modificats' % (nHorarisModificats))
    infos.append(u'%d aules creades' % (nAulesCreades))
    infos.append(u'%d assignatures Creades' % (nAssignaturesCreades))
    infos.append(u'Recorda reprogramar classes segons el nou horari')

    # invocar refer 'imparticions'
    from aula.apps.missatgeria.models import Missatge
    missatge = RECORDA_REPROGRAMAR_CLASSES
    tipus_de_missatge = tipusMissatge(missatge)
    msg = Missatge(
        remitent=usuari,
        text_missatge=RECORDA_REPROGRAMAR_CLASSES,
        enllac="/presencia/regeneraImpartir",
        tipus_de_missatge = tipus_de_missatge)
    msg.afegeix_errors(errors)
    msg.afegeix_warnings(warnings)
    msg.afegeix_infos(infos)
    msg.envia_a_usuari(usuari)

    return {'errors': errors.sort(), 'warnings': warnings, 'infos': infos}


def creaNivellCursGrupDesDeKronowin(file, dia_inici_curs, dia_fi_curs):
    dialect = csv.Sniffer().sniff(file.readline())
    file.seek(0)
    file.readline()
    file.seek(0)
    fieldnames = (
    'assignatura', 'professor', 'grup', 'mati_tarda', 'nivell', 'curs', 'lletra', 'aula', 'unk2', 'dia', 'franja',
    'unk3')
    reader = csv.DictReader(file, fieldnames=fieldnames, dialect=dialect)

    errors = []
    warnings = []
    infos = []

    # cal comprova número de columnes
    aFranges = set([])
    aGrups = set([])
    aProfessors = set([])

    #
    #
    #  PRIMERA PART: comprovar franjes horàries, grups i professors
    #
    #

    if Curs.objects.exists():
        return {'errors': ["Hi ha cursos creats, no es pot realitzar aquesta operació"], 'warnings': warnings,
                'infos': infos}

    Grup2Aula.objects.all().delete()
    for row in reader:
        #
        # comprovar existència franges horàries Kronowin
        #
        nivell = row['nivell']
        curs = row['curs']
        lletra = row['lletra']
        grup = row['grup']

        n, _ = Nivell.objects.get_or_create(nom_nivell=nivell, descripcio_nivell=nivell)
        c, _ = Curs.objects.get_or_create(nom_curs=curs,
                                          nom_curs_complert="{nivell}-{curs}".format(nivell=nivell, curs=curs),
                                          nivell=n, defaults={'data_inici_curs': dia_inici_curs,
                                                              'data_fi_curs': dia_fi_curs})
        g, _ = Grup.objects.get_or_create(nom_grup=lletra, curs=c, defaults={"descripcio_grup": grup, })

        Grup2Aula.objects.get_or_create(grup_kronowin=grup, Grup2Aula=g)

    return {'errors': errors, 'warnings': warnings, 'infos': infos}
