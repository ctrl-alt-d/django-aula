# This Python file uses the following encoding: utf-8

from django.db import models
from aula.apps.usuaris.tools import set_notificacio, set_revisio, get_notif_revisio

class AbstractItemQualitativa(models.Model):
    codi_agrupacio = models.CharField(u'Codi agrupació', max_length=10, blank=True, null=False,
                                      help_text = u"Codi per facilitar l'entrada de la qualitativa. No apareix a l'informe a les famílies." )
    text = models.CharField(u'Item de la Qualitativa', max_length=120, unique=True, null=False, help_text = u"Important: No canvieu mai el significat d'una frase! Canviarieu els resultats de l'avaulació." )
    nivells = models.ManyToManyField( 'alumnes.Nivell', help_text = u"Tria els nivells on aquesta frase pot aparèixer." )
    class Meta:
        abstract = True                
        ordering = ['codi_agrupacio','text']
        verbose_name = u"Frase aval. qualitativa"
        verbose_name_plural = u"Frases aval. qualitativa"
    def __str__(self):
        return  u"{0}.-{1}".format( self.codi_agrupacio, self.text )

class AbstractAvaluacioQualitativa(models.Model):
    nom_avaluacio = models.CharField(u'Avaluació Qualitativa', max_length=120, unique=True, null=False, help_text = u'Ex: Avaluació qualitativa 1ra Avaluació')
    data_obrir_avaluacio = models.DateField( u'Primer dia per entrar Qualitativa', null=False, help_text=u"Data a partir de la qual els professors podran entrar l'avaluació.")
    data_tancar_avaluacio = models.DateField( u'Darrer dia per entrar Qualitativa', null=False, help_text=u"Darrer dia que tenen els professors per entrar la Qualitativa.")
    grups = models.ManyToManyField( 'alumnes.Grup', help_text = u"Tria els grups a avaluar." )    
    data_obrir_portal_families = models.DateField( u'Primer dia per veure els resultats al portal famílies', null=True, blank=True, help_text=u"Els pares podran veure els resultats al portal famílies a partir de la data aquí introduïda.")
    data_tancar_tancar_portal_families = models.DateField( u'Darrer dia per veure els resultats al portal famílies', null=True, blank=True, help_text=u"Els pares podran veure els resultats al portal famílies fins a la data aquí introduïda.")
    class Meta:
        abstract = True        
        ordering = ['data_obrir_avaluacio']  
        verbose_name = u"Avaluació Qualitativa"
        verbose_name_plural = u"Avaluacions Qualitatives"
    def __str__(self):
        return  self.nom_avaluacio    
    
class AbstractRespostaAvaluacioQualitativa(models.Model):
    qualitativa = models.ForeignKey( "avaluacioQualitativa.AvaluacioQualitativa", on_delete=models.CASCADE )
    alumne = models.ForeignKey( 'alumnes.Alumne' , on_delete=models.CASCADE)
    professor = models.ForeignKey('usuaris.Professor', on_delete=models.CASCADE)
    assignatura = models.ForeignKey('assignatures.Assignatura', on_delete=models.CASCADE)
    item = models.ForeignKey( "avaluacioQualitativa.ItemQualitativa", blank=True, null=True , on_delete=models.CASCADE)
    frase_oberta = models.CharField(u'Frase oberta', max_length=120,  help_text = u'Frase oberta', blank=True)
    
    #DEPRECATED vvv
    relacio_familia_revisada = models.DateTimeField( null=True, editable=False )    
    relacio_familia_notificada = models.DateTimeField( null=True, editable=False ) 
    #DEPRECATED ^^^
    
    notificacions_familia = models.ManyToManyField('usuaris.NotifUsuari', db_index=True)
    
    class Meta:
        abstract = True        
        ordering = ['qualitativa','assignatura','alumne' ]
        verbose_name = u"Resposta aval. Qualitativa"
        verbose_name_plural = u"Respostes aval. Qualitative"
        unique_together = (("qualitativa","assignatura","alumne","professor","item",))
    
    def get_resposta_display(self):
        if hasattr(self,'item') and self.item is not None:
            return self.item.text
        else:
            return self.frase_oberta
    
    def set_notificacio(self, notificacio):
        set_notificacio(self, notificacio)
    
    def set_revisio(self, revisio):
        set_revisio(self, revisio)
    
    def get_notif_revisio(self, usuari, fmt_data=None):
        '''
        Retorna str, str amb notificació, revisió de l'usuari
        '''
        return get_notif_revisio(self, usuari, fmt_data)
            
    

    