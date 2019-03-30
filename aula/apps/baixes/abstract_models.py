# This Python file uses the following encoding: utf-8

from django.db import models

class AbstractFeina(models.Model):
    impartir = models.OneToOneField( to = 'presencia.Impartir', on_delete=models.CASCADE  )
    feina_a_fer = models.TextField( blank = True, help_text = u"Explicar on el professor de guardia pot trobar la feina que han de fer els alumnes aquestes dies." )
    professor_fa_guardia = models.ForeignKey( 'usuaris.Professor' , blank=True, null=True, related_name="feina_professor_guardia_set", help_text = u"Professor que farà la guàrdia.", on_delete=models.CASCADE)
    comentaris_per_al_professor_guardia = models.TextField(blank=True, help_text = u"Comentaris per al professor que fa la guàrdia, guardia que substitueix en cas necessari."  )
    comentaris_professor_guardia = models.TextField( blank = True )
    professor_darrera_modificacio = models.ForeignKey( to = 'usuaris.Professor', related_name="feina_professor_audit_set", on_delete=models.CASCADE )
    
    class Meta:
        abstract = True 
        ordering = ('impartir__dia_impartir', 'impartir__horari__hora__hora_inici',  )
        verbose_name = u"Feina baixa"
        verbose_name_plural = u"Feines baixa"    
