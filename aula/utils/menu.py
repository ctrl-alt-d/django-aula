# This Python file uses the following encoding: utf-8
from aula.utils.tools import classebuida
from django.urls import resolve, reverse
from django.contrib.auth.models import Group, User
from aula.apps.usuaris.models import User2Professor, AlumneUser
from django.db.models.aggregates import Count
from django.utils.datetime_safe import date
from aula.apps.usuaris.models import User2Professional
from aula.apps.alumnes.models import Alumne
from datetime import timedelta, datetime
from django.template.defaultfilters import safe
from django.conf import settings
from aula.apps.sortides.models import Sortida

def calcula_menu( user , path ):
    
    if not user.is_authenticated:
        return

    #mire a quins grups està aquest usuari:
    al = Group.objects.get_or_create(name= 'alumne' )[0] in user.groups.all()
    di = not al and Group.objects.get_or_create(name= 'direcció' )[0] in user.groups.all()
    pr = not al and Group.objects.get_or_create(name= 'professors' )[0] in user.groups.all()
    pl = not al and Group.objects.get_or_create(name= 'professional' )[0] in user.groups.all()
    co = not al and Group.objects.get_or_create(name= 'consergeria' )[0] in user.groups.all()
    pg = not al and Group.objects.get_or_create(name= 'psicopedagog' )[0] in user.groups.all()
    so = not al and Group.objects.get_or_create(name= 'sortides' )[0] in user.groups.all()
    tu = not al and pr and ( User2Professor( user).tutor_set.exists() or User2Professor( user).tutorindividualitzat_set.exists() )    
    tots = di or pr or pl or co or al or pg
    
    #Comprovar si té missatges sense llegir
    nMissatges = user.destinatari_set.filter( moment_lectura__isnull = True ).count()
    fa2segons = datetime.now() - timedelta( seconds = 2 )
    nMissatgesDelta = user.destinatari_set.filter( moment_lectura__gte = fa2segons ).count()
    
    #Comprovar si té expulsions sense tramitar o cal fer expulsions per acumulació
    teExpulsionsSenseTramitar= False
    if pr:
        professor = User2Professor( user )
        teExpulsionsSenseTramitar = professor.expulsio_set.exclude( tramitacio_finalitzada = True ).exists() 
        
        #Acumulació Incidències
        if settings.CUSTOM_INCIDENCIES_PROVOQUEN_EXPULSIO and not teExpulsionsSenseTramitar:
            professional = User2Professional( user )
            teExpulsionsSenseTramitar = ( Alumne
                                          .objects
                                          .order_by()
                                          .filter( incidencia__professional = professional, 
                                                   incidencia__tipus__es_informativa = False,
                                                   incidencia__gestionada_pel_tutor = False,
                                                   incidencia__es_vigent = True )
                                          .annotate( n = Count( 'incidencia' ) )
                                          .filter( n__gte = 3 )
                                          .exists()
                                        )
    
    #Comprovar si hi ha una qualitativa oberta
    hiHaUnaQualitativaOberta = False
    if pr:
        from aula.apps.avaluacioQualitativa.models import AvaluacioQualitativa
        hiHaUnaQualitativaOberta = AvaluacioQualitativa.objects.filter(  data_obrir_avaluacio__lte =  date.today(),
                                                                         data_tancar_avaluacio__gte = date.today() ).exists()
    
    menu = { 'items':[], 'subitems':[], 'subsubitems':[], }

    try:
        nom_path = resolve( path ).url_name
    except:
        return menu
    
    menu["esalumne"]=al
    if al:
        alumneuser = AlumneUser.objects.get( id = user.id )
        alumne = alumneuser.getAlumne()
        menu["nomusuari"]= u"Família de {alumne}".format( alumne=alumne.nom )
    else:
        menu["nomusuari"]= user.first_name or user.username 
    
    try:
        menu_id, submenu_id, subsubmenu_id = nom_path.split( '__' )[:3]
    except:
        return menu
    
    arbre_tutoria = (
                      ("Actuacions", 'tutoria__actuacions__list', tu, None, None ),
                      ("Incidències de Tutor", 'tutoria__incidencies__list', tu, None, None ),
                      ("Justificar", 'tutoria__justificar__pre_justificar', tu, None, None ),
                      ("Cartes", 'tutoria__cartes_assistencia__gestio_cartes', tu, None, None ),                                      
                      ("Alumnes", 'tutoria__alumnes__list', tu, None, None ),
                      ("Assistència", 'tutoria__assistencia__list_entre_dates', tu, None, None ),                                      
                      ("Informe", 'tutoria__alumne__informe_setmanal', tu, None, None ),                                      
                      ("Portal", 'tutoria__relacio_families__dades_relacio_families', tu, None, None ),
                      ("Seguiment", 'tutoria__seguiment_tutorial__formulari', tu, None, None ),
                    )
    if settings.CUSTOM_TUTORS_INFORME:
        arbre_tutoria += (
                      ("Impressió Faltes i Incid.", 'tutoria__informe__informe_faltes_incidencies', tu, None, None ),                                      
                    )
        
    if hasattr(settings, 'CUSTOM_MODUL_SORTIDES_ACTIU' ) and settings.CUSTOM_MODUL_SORTIDES_ACTIU and ( di or pr ):
        professor = User2Professor( user )
        filtre = [ 'P', 'R', ]
        te_sortides_actives = ( Sortida
                       .objects
                       .exclude( estat = 'E' )
                       .filter( estat__in = filtre )
                       .filter( data_inici__gte = datetime.now() )
                       .filter( tutors_alumnes_convocats = professor )
                       .exists()
                      )    
        arbre_tutoria += (
                      ("Sortides", 'tutoria__justificarSortida__list', tu, ( u'!', 'info' ) if te_sortides_actives else None, None
                      ),                                      
                    )



    
    arbre1 = (

               #--Consergeria--------------------------------------------------------------------------
               ('consergeria', 'Consergeria', 'consergeria__missatges__envia_tutors', co, None,
                  (
                      ("Missatge a tutors", 'consergeria__missatges__envia_tutors', co, None, None ),
                      ("Incidència per retard", 'consergeria__incidencia__onbehalf', co, None, None ),

                   )
               ),
        
               #--Aula--------------------------------------------------------------------------
               #  id,    nom     vista                 seg      label
               ('aula', 'Aula', 'blanc__blanc__blanc', pr, teExpulsionsSenseTramitar or hiHaUnaQualitativaOberta ,
                  (
                      ("Presencia", 'aula__horari__horari', pr, None, None ),
                      #("Alumnes", 'aula__alumnes__alumnes_i_assignatures', pr, None, None ),

                      ("Alumnes", 'aula__alumnes__blanc', pr, None,
                          ( 
                            ("Els meus alumnes", 'aula__alumnes__alumnes_i_assignatures', pr, None),
                          ),                        
                      ),                                                            

                      ("Incidències", 'aula__incidencies__blanc', pr, ( u'!', 'info' ) if teExpulsionsSenseTramitar else None,
                          (
                            ("Incidències", 'aula__incidencies__les_meves_incidencies', pr, ( u'!', 'info' ) if teExpulsionsSenseTramitar else None),
                            ("Nova Incidència (fora d'aula)", 'aula__incidencies__posa_incidencia', pr, None ),
                            ("Recull Expulsió", 'aula__incidencies__posa_expulsio', pr, None),
                          ),                        
                      ),                                      
                      ("Matèries", 'aula__materies__blanc', pr, None, 
                          ( 
                            ("Llistat entre dates", 'aula__materies__assistencia_llistat_entre_dates', pr, None),
                            ("Calculadora UF", 'aula__materies__calculadora_uf', pr, None )
                          )
                      ),         
                      ("Qualitativa", 'aula__qualitativa__les_meves_avaulacions_qualitatives', pr, ( u'!', 'info' ) if hiHaUnaQualitativaOberta else None, None ),
                   )
               ),

               #--Tutoria--------------------------------------------------------------------------
               ('tutoria', 'Tutoria', 'tutoria__actuacions__list', tu, None,
                   arbre_tutoria
               ),

               #--Gestió--------------------------------------------------------------------------
               ('gestio', 'Gestió', 'gestio__reserva_aula__list', co or pl, None,
                  (
                      ("Reserva Aula", 'gestio__reserva_aula__list', co or pl, None, None),                                        
                      ("Cerca Alumne", 'gestio__usuari__cerca', co or pl, None, None),
                      ("Cerca Professor", 'gestio__professor__cerca', co or pl, None, None),  
                   )
               ),
                            
               #--psicopedagog--------------------------------------------------------------------------
               ('psico', 'Psicopedagog', 'psico__informes_alumne__list', pg or di, None,
                  (
                      ("Alumne", 'psico__informes_alumne__list', pg or di, None, None ),
                      ("Actuacions", 'psico__actuacions__list', pg or di, None, None ),
                   )
               ),

               #--Coord.Pedag--------------------------------------------------------------------------
               ('coordinacio_pedagogica', 'Coord.Pedag', 'coordinacio_pedagogica__qualitativa__blanc', di, None,
                  (
                      ("Qualitativa", 'coordinacio_pedagogica__qualitativa__blanc', di, None, 
                          (
                              ("Avaluacions", 'coordinacio_pedagogica__qualitativa__avaluacions', di , None  ),
                              ("Items", 'coordinacio_pedagogica__qualitativa__items', di , None  ),
                              ("Resultats", 'coordinacio_pedagogica__qualitativa__resultats_qualitatives', di , None  ),
                          ),
                      ),
                      ("Seguiment Tutorial", "coordinacio_pedagogica__seguiment_tutorial__preguntes", di, None, None ),
                   ),
               ),

               #--Coord.Alumnes--------------------------------------------------------------------------
               ('coordinacio_alumnes', 'Coord.Alumnes', 'coordinacio_alumnes__ranking__list', di, None,
                  (
                      ("Alertes Incid.", 'coordinacio_alumnes__ranking__list', di, None, None ),
                      ("Alertes Assist.", 'coordinacio_alumnes__assistencia_alertes__llistat', di, None, None ),
                      ("Cartes", 'coordinacio_alumnes__assistencia__cartes', di, None, None ),
                      ("Sancions", 'coordinacio_alumnes__sancions__sancions', di, None, None ),
                      ("Passa llista grup", 'coordinacio_alumnes__presencia__passa_llista_a_un_grup_tria', di, None, None ),
                      ("Impressió Faltes i Incid.", 'coordinacio_alumnes__alumne__informe_faltes_incidencies', di, None, None ),
                      #amorilla@xtec.cat
                      ("Indicadors", 'coordinacio_alumnes__indicadors__llistat', di, None, None ),
                   )
               ),

               #--Coord.Profess.--------------------------------------------------------------------------
               ('professorat', 'Coord.Prof', 'professorat__baixes__blanc', di, None,
                  (
                      ("Feina Absència", 'professorat__baixes__blanc', di, None,
                         (
                            ('Posar feina', 'professorat__baixes__complement_formulari_tria', di, None),
                            ('Imprimir feina', 'professorat__baixes__complement_formulari_impressio_tria' ,di, None),
                         ), 
                      ),
                      ("Tutors", 'professorat__tutors__blanc', di, None,
                         (
                            ('Tutors Grups', 'professorat__tutors__tutors_grups', di, None),
                            ('Tutors individualitzat', 'professorat__tutors__tutors_individualitzats', di, None),
                         ), 
                      ),
                      ("Professors", 'professorat__professors__list', di, None, None ),
                      ("Estat Tramitació Exp.", 'professorat__expulsions__control_tramitacio', di, None, None ),
                   ),
               ),

               #--Administració--------------------------------------------------------------------------
               ('administracio', 'Admin', 'administracio__sincronitza__blanc', di, None,
                  (
                      ("Sincronitza", 'administracio__sincronitza__blanc', di, None, 
                        (
                          ("Alumnes ESO/BAT", 'administracio__sincronitza__esfera', di , None  ),
                          ("Alumnes Cicles", 'administracio__sincronitza__saga', di, None),
                          ("Horaris", 'administracio__sincronitza__kronowin', di , None  ),
                          ("Aules", 'gestio__aula__assignacomentari', di, None),
                          ("Reprograma", 'administracio__sincronitza__regenerar_horaris', di , None  ),
                        ),
                      ),
                      ("Reset Passwd", 'administracio__professorat__reset_passwd', di, None, None ),
                      ("Càrrega Inicial", 'administracio__configuracio__carrega_inicial', di, None, None ),
                      ("Promocions", 'administracio__promocions__llista', di, None, None),
#                      ("Nou Alumne", 'administracio__alumnes__noualumne', di, None, None),
# Aquesta pantalla encara no té implementada la seva funcionalitat.
# Queda pendent acabar-la, o eliminar-la de l'aplicació.
                   )
               ),
        
               #--relacio_families--------------------------------------------------------------------------
               ('relacio_families', u'Famílies', 'relacio_families__informe__el_meu_informe', al, None,
                  (
                      ("Informe", 'relacio_families__informe__el_meu_informe', al, None, None ),
                      ("Paràmetres", 'relacio_families__configuracio__canvi_parametres', al, None, None ),
                   )
               ),
             )
    
    arbre2 = (

               #--Varis--------------------------------------------------------------------------
               ('varis', 'Ajuda i Avisos', 'varis__about__about' if al else 'varis__elmur__veure', tots, nMissatges > 0,
                  (
                      ("Notificacions", 'varis__elmur__veure', di or pr or pl or co or pg , ( nMissatgesDelta, 'info' if nMissatgesDelta < 10 else 'danger' ) if nMissatgesDelta >0 else None, None ),
                      ("Missatge a professorat o PAS", 'varis__prof_i_pas__envia_professors_i_pas', pr or pl or co, None, None ),
                      ("Avisos de Seguretat", 'varis__avisos__envia_avis_administradors', tots, None, None ),
                      ("About", 'varis__about__about', tots, None, None ),
                   )
               ),

             )
    
    arbreSortides = ()
    if hasattr(settings, 'CUSTOM_MODUL_SORTIDES_ACTIU' ) and settings.CUSTOM_MODUL_SORTIDES_ACTIU and ( di or pr ):
        
        filtre = []
        socEquipDirectiu = User.objects.filter( pk=user.pk, groups__name = 'direcció').exists()
        socCoordinador = User.objects.filter( pk=user.pk, groups__name__in = [ 'sortides'] ).exists()
    
        #si sóc equip directiu només les que tinguin estat 'R' (Revisada pel coordinador)
        if socEquipDirectiu:
            filtre.append('R')
        #si sóc coordinador de sortides només les que tinguin estat 'P' (Proposada)
        if socCoordinador:
            filtre.append('P')
        
        n_avis_sortides = ( Sortida
                           .objects
                           .exclude( estat = 'E' )
                           .filter( estat__in = filtre )
                           .distinct()
                           .count()
                          )    
        
        n_avis_sortides_meves = ( Sortida
                           .objects
                           .filter( estat = 'E' )
                           .filter( professor_que_proposa__pk = user.pk )
                           .distinct( )
                           .count()
                          )  
        
        arbreSortides = (
               #--Varis--------------------------------------------------------------------------
               ('sortides', 'Activitats', 'sortides__meves__list', di or pr, n_avis_sortides + n_avis_sortides_meves> 0,
                  (
                      (u"Històric", 'sortides__all__list', di or so, None, None ),
                      (u"Gestió d'activitats", 'sortides__gestio__list', di or so, ( n_avis_sortides ,'info', ) if n_avis_sortides > 0 else None, None ),
                      (u"Les meves propostes d'activitats", 'sortides__meves__list', pr, ( n_avis_sortides_meves ,'info', ) if n_avis_sortides_meves > 0 else None, None ),
                   )
               ),                            
                         )
    
    arbre = arbre1 + arbreSortides + arbre2
    
    for item_id, item_label, item_url, item_condicio, alerta , subitems in arbre:

        if not item_condicio:
            continue
        actiu = ( menu_id == item_id )
        item = classebuida()
        item.label = item_label
        item.url = reverse( item_url )
        item.active = 'active' if actiu else ''
        item.alerta = alerta
        menu['items'].append( item )
        
        if actiu:
            for subitem_label, subitem_url, subitem__condicio, medalla, subsubitems in subitems:
                if not subitem__condicio:
                    continue
                actiu = ( submenu_id == subitem_url.split('__')[1] )
                subitem = classebuida()
                subitem.label = safe( subitem_label )
                subitem.url = reverse( subitem_url ) 
                subitem.active = 'active' if actiu else ''
                if medalla:
                    omedalla = classebuida()
                    omedalla.valor = medalla[0]
                    omedalla.tipus = medalla[1]
                    subitem.medalla = omedalla
                menu['subitems'].append(subitem)
                subitem.subsubitems = []
                if subsubitems:
                    for subitem_label, subitem_url, subitem_condicio, subitem_medalla in subsubitems:
                        subsubitem = classebuida()
                        subsubitem.label = safe( subitem_label )
                        subsubitem.url = reverse( subitem_url ) 
                        if subitem_medalla:
                            omedalla = classebuida()
                            omedalla.valor = subitem_medalla[0]
                            omedalla.tipus = subitem_medalla[1]
                            subsubitem.medalla = omedalla
                        subitem.subsubitems.append(subsubitem)
                    if actiu and subsubmenu_id == 'blanc':
                        menu['subsubitems'] = subitem.subsubitems

    return menu


'''

professorat__baixes__complement_formulari_impressio_tria
professorat__baixes__complement_formulari_imprimeix
professorat__baixes__complement_formulari_omple
professorat__baixes__complement_formulari_tria
professorat__professors__list
professorat__tutors__gestio_alumnes_tutor
professorat__tutors__tutors_grups
professorat__tutors__tutors_individualitzats


coordinacio_alumnes__assistencia_alertes__llistat
coordinacio_alumnes__assistencia__cartes
coordinacio_alumnes__sancions__carta
coordinacio_alumnes__sancions__edicio
coordinacio_alumnes__sancions__esborrar
coordinacio_alumnes__sancions__sancionar
coordinacio_alumnes__sancions__sancio
coordinacio_alumnes__sancions__sancio
coordinacio_alumnes__sancions__sancions
coordinacio_alumnes__sancions__sancions
coordinacio_alumnes__sancions__sancions_excel
coordinacio_alumnes__presencia__passa_llista_a_un_grup_tria
coordinacio_alumnes__ranking__list
coordinacio_alumnes__seguiment_tutorial__preguntes
coordinacio_alumnes__indicadors__llistat

administracio__configuracio__assigna_franges_kronowin
administracio__configuracio__assigna_grups
administracio__configuracio__assigna_grups_kronowin
administracio__professorat__reset_passwd
administracio__sincronitza__duplicats
administracio__sincronitza__fusiona
administracio__sincronitza__kronowin
administracio__sincronitza__regenerar_horaris
administracio__sincronitza__saga
administracio__sincronitza__esfera

coordinacio_pedagogica__qualitativa__avaluacions
coordinacio_pedagogica__qualitativa__items
coordinacio_pedagogica__qualitativa__report

aula__materies__assistencia_llistat_entre_dates
aula__materies__calculadora_uf

aula__horari__afegir_alumnes
aula__horari__afegir_guardia
 aula__horari__alumnes_i_assignatures
aula__horari__elimina_incidencia
aula__horari__esborrar_guardia
aula__horari__feina
aula__horari__horari
aula__horari__horari
aula__horari__hora_sense_alumnes
aula__horari__passa_llista
aula__horari__posa_incidencia
aula__horari__treure_alumnes
aula__incidencies__edita_expulsio
aula__incidencies__elimina_incidencia
aula__incidencies__les_meves_incidencies
 aula__incidencies__posa_expulsio
aula__incidencies__posa_expulsio_per_acumulacio
aula__incidencies__posa_expulsio_w2
 aula__incidencies__posa_incidencia
aula__qualitativa__entra_qualitativa
aula__qualitativa__les_meves_avaulacions_qualitatives
aula__qualitativa__resultats_qualitatives


tutoria__actuacions__alta
tutoria__actuacions__edicio
tutoria__actuacions__esborrat
 tutoria__actuacions__list
tutoria__actuacions__list_entre_dates
tutoria__alumne__detall
tutoria__alumne__informe_faltes_incidencies
tutoria__alumne__informe_setmanal
tutoria__alumne__informe_setmanal_print
tutoria__alumnes__list
tutoria__cartes_assistencia__esborrar_carta
tutoria__cartes_assistencia__gestio_cartes
tutoria__cartes_assistencia__imprimir_carta
tutoria__cartes_assistencia__imprimir_carta_no_flag
tutoria__cartes_assistencia__nova_carta
tutoria__justificar__by_pk_and_date
tutoria__justificar__justificador
tutoria__justificar__next
 tutoria__justificar__pre_justificar
tutoria__obsolet__treure
tutoria__relacio_families__bloqueja_desbloqueja
tutoria__relacio_families___configura_connexio
tutoria__relacio_families__dades_relacio_families
tutoria__relacio_families__envia_benvinguda
 tutoria__seguiment_tutorial__formulari
        


nologin__usuari__login
nologin__usuari__recover_password
nologin__usuari__send_pass_by_email
obsolet__tria_alumne
psico__informes_alumne
relacio_families__configuracio__canvi_parametres
'relacio_families__informe__el_meu_informe'),
relacio_families__informe__el_meu_informe
triaAlumneAlumneAjax
triaAlumneCursAjax
triaAlumneGrupAjax

usuari__dades__canvi
usuari__dades__canvi_passwd
usuari__impersonacio__impersonacio
usuari__impersonacio__reset

varis__todo__del
varis__todo__edit
varis__todo__edit_by_pk
varis__todo__list
'''
        
                
