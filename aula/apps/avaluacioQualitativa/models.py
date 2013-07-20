# This Python file uses the following encoding: utf-8
from aula.apps.avaluacioQualitativa.abstract_models import AbstractItemQualitativa,\
    AbstractRespostaAvaluacioQualitativa, AbstractAvaluacioQualitativa

from aula.apps.avaluacioQualitativa.business_rules.respostaavaluacioqualitativa import respostaAvaluacioQualitativa_pre_delete,\
    respostaAvaluacioQualitativa_pre_save, respostaAvaluacioQualitativa_clean

class ItemQualitativa(AbstractItemQualitativa):
    pass

class AvaluacioQualitativa(AbstractAvaluacioQualitativa):
    pass

class RespostaAvaluacioQualitativa(AbstractRespostaAvaluacioQualitativa):
    def clean(self):
        respostaAvaluacioQualitativa_clean( self )    
            
# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #
from django.db.models.signals import post_save, pre_save, pre_delete

pre_delete.connect(respostaAvaluacioQualitativa_pre_delete, sender= RespostaAvaluacioQualitativa)
pre_save.connect(respostaAvaluacioQualitativa_pre_save, sender = RespostaAvaluacioQualitativa )    
    
    