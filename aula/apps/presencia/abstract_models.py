# This Python file uses the following encoding: utf-8

from django.db import models
from datetime import datetime
from django.apps import apps
#consultes
from django.db.models import Q
from aula.utils.tools import unicode

class AbstractImpartir(models.Model):
    horari = models.ForeignKey('horaris.Horari', db_index=True, on_delete=models.CASCADE)
    professor_guardia = models.ForeignKey('usuaris.Professor', null=True,  blank=True, related_name='professor_guardia', on_delete=models.PROTECT)
    professor_passa_llista = models.ForeignKey('usuaris.Professor', null=True,  blank=True, db_index=True, related_name='professor_passa_llista', on_delete=models.PROTECT)
    dia_impartir = models.DateField(db_index=True)
    dia_passa_llista = models.DateTimeField(null=True, blank=True)
    comentariImpartir = models.TextField(null=False, blank=True, default='')
    pot_no_tenir_alumnes = models.BooleanField(default=False)
    reserva = models.ForeignKey('aules.ReservaAula', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True
        verbose_name = u'Impartir classe'
        verbose_name_plural = u'Impartir classes'
        unique_together = (("dia_impartir","horari"))

    def __str__(self):
        canviaula = u""
        if self.canvi_aula_respecte_horari:
            canviaula = u" amb canvi d'aula a la {aula}".format(aula=self.get_nom_aula)
        resposta = u"{dia}: {horari}{canviaula}".format(
                                dia = self.dia_impartir.strftime( "%d/%m/%Y"),
                                horari = self.horari,
                                canviaula = canviaula,
        )
        return resposta

    @property
    def canvi_aula_respecte_horari(self):
        te_reserva =  bool(self.reserva)
        return te_reserva and self.reserva.aula != self.horari.aula

    @property
    def get_nom_aula(self):
        te_reserva =  bool(self.reserva)
        if te_reserva:
            alarma = "" #"" !" if self.reserva.es_reserva_manual else ""
            return u"{aula}{alarma}".format( aula= self.reserva.aula.nom_aula, alarma=alarma )
        else:
            return self.horari.aula.nom_aula if self.horari.aula else ""

    def esFutur(self):
        data = datetime( year = self.dia_impartir.year, 
                         month = self.dia_impartir.month,
                         day = self.dia_impartir.day,
                         hour =  self.horari.hora.hora_inici.hour, 
                         minute = self.horari.hora.hora_inici.minute,
                         second = 0 )
        return data > datetime.now()

    def esReservaManual(self):
        te_reserva = bool(self.reserva)
        if te_reserva:
            return self.reserva.es_reserva_manual
        else:
            return False

    def esAvui(self):
        from datetime import date
        data = date( year = self.dia_impartir.year, 
                         month = self.dia_impartir.month, 
                         day = self.dia_impartir.day,
                          )
        return data == date.today()
    
    def diaHora(self):
        diaHora = None
        try:
            diaHora =  datetime(  
                            year = self.dia_impartir.year, 
                            month = self.dia_impartir.month, 
                            day = self.dia_impartir.day, 
                            hour = self.horari.hora.hora_inici.hour,  
                            minute = self.horari.hora.hora_inici.minute,  
                        )
        except:
            pass
        return diaHora
    
    def resum(self):
        nAlumnes = self.controlassistencia_set.count()
        nIncidencies = self.controlassistencia_set.filter( incidencia__isnull = False   ).count()
        nExpulsions = self.controlassistencia_set.filter( expulsio__isnull = False   ).count()
        return u'Al:{0} In:{1} Ex:{2}'.format(nAlumnes,  nIncidencies, nExpulsions )
    
    def hi_ha_nulls(self):
        return ( self
                 .controlassistencia_set
                 .filter( estat__isnull = True   )
                 .exclude( nohadeseralaula__isnull = False )
                 .order_by( )
                 .distinct( )
                 .exists()
                )
    
    def color(self):
        if self.dia_passa_llista:
            if self.hi_ha_nulls():
                return u'warning'
            else:
                return u'success'
        elif self.pot_no_tenir_alumnes:
            return u'success'
        elif self.esAvui():
            return u'info' 
        elif self.esFutur():
            return u'default' 
        else:
            if self.hi_ha_nulls():
                return u'danger'
            else:
                return u'success'


    @property
    def hi_ha_alumnes_amb_activitat_programada(self):


        #
        q_sortida_comenca_mes_tard = ( Q( controlassistencia__alumne__sortides_confirmades__data_inici__gt =  self.dia_impartir ) |
                                       ( Q( controlassistencia__alumne__sortides_confirmades__franja_inici__hora_inici__gt =  self.horari.hora.hora_inici ) &
                                         Q( controlassistencia__alumne__sortides_confirmades__data_inici =  self.dia_impartir )
                                       )
                                     )
        q_sortida_acaba_abans = ( Q( controlassistencia__alumne__sortides_confirmades__data_fi__lt =  self.dia_impartir ) |
                                       ( Q( controlassistencia__alumne__sortides_confirmades__franja_fi__hora_fi__lt =  self.horari.hora.hora_fi ) &
                                         Q( controlassistencia__alumne__sortides_confirmades__data_inici =  self.dia_impartir )
                                       )
                                     )
        
        
        q_fora_de_rang = ( q_sortida_comenca_mes_tard | q_sortida_acaba_abans  ) 

        #q activitat inclou nens meus
        q_es_meu = Q( id = self.id )    
            
        #tinc alumnes?
        
        ######### Ho comento! la query és massa béstia. Cal optimitzar!
        
        hi_ha_alumnes_a_la_sortida = False and ( self.__class__
                                          .objects
                                          .filter( ~q_fora_de_rang & q_es_meu )
                                          .exists()
                                        )               

#         print (  self.__class__
#                                           .objects
#                                           .filter( ~q_fora_de_rang & q_es_meu ).query )
        
        return False and hi_ha_alumnes_a_la_sortida

class AbstractEstatControlAssistencia(models.Model):
    codi_estat = models.CharField( max_length=1, unique=True)
    nom_estat = models.CharField(max_length=45, unique=True)
    pct_ausencia = models.IntegerField(  default=0, null=False, blank=False, help_text=u"100=Falta tota l'hora, 0=No és falta assistència. Aquest camp serveix per que els retrassos es puguin comptar com a falta o com un percentatge de falta." )
    
    class Meta:
        abstract = True
        verbose_name = u"Estat control d'assistencia"
        verbose_name_plural = u"Estats control d'assistencia"
        
    def __str__(self):
        return self.nom_estat    
    

class AbstractControlAssistencia(models.Model):
    alumne = models.ForeignKey(to = 'alumnes.Alumne',  db_index=True, on_delete=models.CASCADE)
    estat = models.ForeignKey('presencia.EstatControlAssistencia',  db_index=True, null=True, blank=True, on_delete=models.CASCADE)
    impartir = models.ForeignKey('presencia.Impartir', db_index=True, on_delete=models.CASCADE)
    professor = models.ForeignKey('usuaris.Professor', null=True, blank=True, on_delete=models.CASCADE)
    
    swaped = models.BooleanField(default=False)
    estat_backup = models.ForeignKey('presencia.EstatControlAssistencia', related_name='controlassistencia_as_bkup', db_index=True, null=True, blank=True, on_delete=models.CASCADE)
    professor_backup = models.ForeignKey('usuaris.Professor', related_name='controlassistencia_as_bkup', null=True, blank=True, on_delete=models.CASCADE)
    
    relacio_familia_revisada = models.DateTimeField( null=True )    
    relacio_familia_notificada = models.DateTimeField( null=True ) 
    
    comunicat = models.ForeignKey('missatgeria.Missatge', null=True, blank=True, db_index=True, on_delete=models.PROTECT)
    
    class Meta:
        abstract = True
        verbose_name = u'Entrada al Control d\'Assistencia'
        verbose_name_plural = u'Entrades al Control d\'Assistencia'
        unique_together = (("alumne", "impartir"))
        
    def __str__(self):
        return unicode(self.alumne) + u' -> '+ unicode(self.estat)

    def esPrimeraHora(self):
        ControlAssistencia = self.__class__
        return not ( ControlAssistencia
                     .objects
                     .filter( alumne = self.alumne,
                              impartir__dia_impartir = self.impartir.dia_impartir,
                              impartir__horari__hora__hora_inici__lt = self.impartir.horari.hora.hora_inici
                            )
                     .exists()
                    )

    @property
    def descripcio(self):
        text=u'{0}:{1}  Prof.: {2}'.format( self.estat or "", self.impartir.horari.assignatura if self.impartir.horari else "" ,
                                            self.professor or ( self.impartir.horari.professor if self.impartir.horari else "" ) )
        if self.comunicat:
            text=text+". "+self.comunicat.text_missatge
        return text


class AbstractNoHaDeSerALAula(models.Model):
    #cal recalcular-lo en aquesta casos:
    #  - crear control assistència
    #  - afegir ó modificar expulsió
    #  - afegir ó modificar sortida
    
    EXPULSAT_DEL_CENTRE = 'E'
    SORTIDA = 'A'
    ANULLADA= 'L'
    
    MOTIUS_CHOICE = ( 
                       (EXPULSAT_DEL_CENTRE, u"Expulsat del centre",),
                       (SORTIDA,u"Activitat",),
                       (ANULLADA, u"Classe Anul·lada"),
                     )
    
    motiu = models.CharField(  max_length=5, choices =  MOTIUS_CHOICE )
    control=models.ForeignKey(to = 'presencia.ControlAssistencia', on_delete=models.CASCADE, db_index=True)
    sancio =models.ForeignKey(to = 'incidencies.Sancio',blank=True, null=True, on_delete=models.CASCADE, db_index=True)
    sortida =models.ForeignKey(to = 'sortides.Sortida',blank=True, null=True, on_delete=models.CASCADE, db_index=True)
    
    
    
    class Meta:
        abstract = True
        verbose_name = u'Motiu no ha està pressent'
        verbose_name_plural = u'Motius no presència a l\'aula'
        
    def __str__(self):
        return unicode(self.control.alumne) + u' -> '+ unicode(self.get_motiu_display() )    



