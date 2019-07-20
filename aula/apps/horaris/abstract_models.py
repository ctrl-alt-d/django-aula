
# This Python file uses the following encoding: utf-8

from django.db import models
from django.apps import apps
from aula.utils.tools import unicode


class AbstractDiaDeLaSetmana(models.Model):
    n_dia_uk = models.IntegerField(u'Número de dia de la setmana a UK (0=diumenge)', unique=True) 
    n_dia_ca = models.IntegerField(u'Número de dia de la setmana aquí (0=dilluns)', unique=True) 
    dia_2_lletres = models.CharField("Dia",max_length=6, unique=True)
    dia_de_la_setmana = models.CharField("Dia de la setmana",max_length=45, unique=True)
    es_festiu = models.BooleanField(u'És festiu?')
    class Meta:
        abstract = True
        ordering = ['n_dia_ca']
        verbose_name = u'Dia de la Setmana'
        verbose_name_plural = u'Dies de la Setmana'
    def __str__(self):
        return self.dia_de_la_setmana

class AbstractFranjaHoraria(models.Model):
    hora_inici = models.TimeField(unique=True) 
    hora_fi = models.TimeField(unique=True)
    nom_franja = models.CharField(max_length=45, blank=True)  
    class Meta:
        abstract = True
        ordering = ['hora_inici']
        verbose_name = u'Franja Horària'
        verbose_name_plural = u'Franges Horàries'
    def __str__(self):
        return  self.nom_franja if self.nom_franja else  unicode(self.hora_inici)[0:5] + ' a ' + unicode(self.hora_fi)[0:5]
    def text_hora_inici(self):
        return self.hora_inici.strftime("%H:%M");

#------------------------------------------------------------------------------------------------

class AbstractHorari(models.Model):
    assignatura = models.ForeignKey('assignatures.Assignatura', null=True, blank=True, on_delete=models.CASCADE)
    professor = models.ForeignKey('usuaris.Professor', null=True,  blank=True, db_index=True, on_delete=models.CASCADE)
    grup = models.ForeignKey(to='alumnes.Grup', null=True,  blank=True, db_index=True, on_delete=models.CASCADE)
    dia_de_la_setmana = models.ForeignKey('horaris.DiaDeLaSetmana', on_delete=models.CASCADE )
    hora = models.ForeignKey( 'horaris.FranjaHoraria', on_delete=models.CASCADE )
    nom_aula = models.CharField(max_length=45, blank=True)
    aula = models.ForeignKey('aules.Aula', null=True, blank=True, on_delete=models.SET_NULL)
    es_actiu = models.BooleanField()
    estat_sincronitzacio = models.CharField(max_length=3, blank=True)

    @property
    def get_nom_aula(self):
        return self.aula.nom_aula if bool(self.aula) else u""

    class Meta:
        abstract = True
        ordering=['es_actiu', 'professor','dia_de_la_setmana__n_dia_ca','hora__hora_inici']
        verbose_name = u"Entrada a l'Horari"
        verbose_name_plural = u"Entrades a l'Horari"

    def __str__(self):
        obsolet = u'(Obsolet:) ' if not self.es_actiu else ''
        aula = u" a l'aula " + self.get_nom_aula if self.get_nom_aula else ''
        grup = u' al grup ' + unicode( self.grup) if self.grup else ''
        return obsolet + u'El professor ' + unicode( self.professor) + u' imparteix ' + unicode(self.assignatura) + ' el ' + unicode( self.dia_de_la_setmana) + ' de ' +  unicode(self.hora) + aula + grup

    def grupsPotencials(self):
        grups_potencials = None
        codi_ambit = self.assignatura.tipus_assignatura.ambit_on_prendre_alumnes if self.assignatura.tipus_assignatura is not None else 'G'
        Grup = apps.get_model( 'alumnes','Grup')
        if codi_ambit == 'I':
            grups_potencials= Grup.objects.all( )
        elif codi_ambit == 'N':
            grups_potencials= Grup.objects.filter( curs__nivell = self.grup.curs.nivell  )
        elif codi_ambit == 'C':
            grups_potencials= Grup.objects.filter( curs = self.grup.curs  )
        elif codi_ambit == 'G':
            if self.grup:
                grups_potencials=Grup.objects.filter( pk = self.grup.pk  )
            else:
                grups_potencials=Grup.objects.none()
        return grups_potencials



#------------------------------------------------------------------------------------------------

class AbstractFestiu(models.Model):
    curs = models.ForeignKey('alumnes.Curs', null=True, blank=True, on_delete=models.CASCADE)
    data_inici_festiu = models.DateField()
    franja_horaria_inici = models.ForeignKey('horaris.FranjaHoraria', related_name='hora_inici_festiu', on_delete=models.CASCADE )
    data_fi_festiu = models.DateField()
    franja_horaria_fi = models.ForeignKey('horaris.FranjaHoraria', related_name='hora_fi_festiu', on_delete=models.CASCADE)
    descripcio = models.CharField(max_length=45)
    
    class Meta:
        abstract = True
        ordering = ['data_inici_festiu','franja_horaria_inici']
        verbose_name = u'Entrada al calendari de festius'
        verbose_name_plural = u'Entrades al calendari de festius'

    def __str__(self):
        curs =  u'(' + unicode( self.curs ) + u')' if self.curs else u''
        return  self.descripcio + curs
    



    

