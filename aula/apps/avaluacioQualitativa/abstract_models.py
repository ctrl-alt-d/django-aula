# This Python file uses the following encoding: utf-8

from django.db import models

class AbstractItemQualitativa(models.Model):
    text = models.CharField(u'Item de la Qualitativa', max_length=120, unique=True, null=False, help_text = u"Important: No canvieu mai el significat d'una frase! Canviarieu els resultats de l'avaulació." )
    nivells = models.ManyToManyField( 'alumnes.Nivell', help_text = u"Tria els nivells on aquesta frase pot aparèixer." )
    class Meta:
        abstract = True                
        ordering = ['text'] 
        verbose_name = u"Frase aval. qualitativa"
        verbose_name_plural = u"Frases aval. qualitativa"
    def __unicode__(self):
        return  self.text

class AbstractAvaluacioQualitativa(models.Model):
    nom_avaluacio = models.CharField(u'Avaluació Qualitativa', max_length=120, unique=True, null=False, help_text = u'Ex: Avaluació qualitativa 1ra Avaluació')
    data_obrir_avaluacio = models.DateField( u'Primer dia per entrar Qualitativa',unique=True, null=False, help_text=u"Data a partir de la qual els professors podran entrar l'avaluació.")
    data_tancar_avaluacio = models.DateField( u'Darrer dia per entrar Qualitativa',unique=True, null=False, help_text=u"Darrer dia que tenen els professors per entrar la Qualitativa.")
    grups = models.ManyToManyField( 'alumnes.Grup', help_text = u"Tria els grups a avaluar." )    
    data_obrir_portal_families = models.DateField( u'Primer dia per veure els resultats al portal famílies', null=True, blank=True, help_text=u"Els pares podran veure els resultats al portal famílies a partir de la data aquí introduïda.")
    data_tancar_tancar_portal_families = models.DateField( u'Darrer dia per veure els resultats al portal famílies', null=True, blank=True, help_text=u"Els pares podran veure els resultats al portal famílies fins a la data aquí introduïda.")
    class Meta:
        abstract = True        
        ordering = ['data_obrir_avaluacio']  
        verbose_name = u"Avaluació Qualitativa"
        verbose_name_plural = u"Avaluacions Qualitatives"
    def __unicode__(self):
        return  self.nom_avaluacio    
    
class AbstractRespostaAvaluacioQualitativa(models.Model):
    qualitativa = models.ForeignKey( "avaluacioQualitativa.AvaluacioQualitativa" )
    alumne = models.ForeignKey( 'alumnes.Alumne' )
    professor = models.ForeignKey('usuaris.Professor')
    assignatura = models.ForeignKey('assignatures.Assignatura')
    item = models.ForeignKey( "avaluacioQualitativa.ItemQualitativa", blank=True, null=True )
    frase_oberta = models.CharField(u'Frase oberta', max_length=120,  help_text = u'Frase oberta', blank=True)
    
    relacio_familia_revisada = models.DateTimeField( null=True, editable=False )    
    relacio_familia_notificada = models.DateTimeField( null=True, editable=False ) 
        
    class Meta:
        abstract = True        
        ordering = ['qualitativa','assignatura','alumne' ]
        verbose_name = u"Resposta aval. Qualitativa"
        verbose_name_plural = u"Respostes aval. Qualitative"
        unique_together = (("qualitativa","assignatura","alumne","professor","item",))
    

    

    