# This Python file uses the following encoding: utf-8


from django import forms as forms
from aula.apps.avaluacioQualitativa.models import RespostaAvaluacioQualitativa,\
    AvaluacioQualitativa


class qualitativaItemsForm(forms.Form):  
    alumne = forms.CharField( widget = forms.TextInput( attrs={'readonly': True} ) ) 
    q1 = forms.ModelChoiceField( queryset = RespostaAvaluacioQualitativa.objects.none(), required = False  )
    q2 = forms.ModelChoiceField( queryset = RespostaAvaluacioQualitativa.objects.none(), required = False  )
    q3 = forms.ModelChoiceField( queryset = RespostaAvaluacioQualitativa.objects.none(), required = False  )
    #q4 = forms.ModelChoiceField( queryset = RespostaAvaluacioQualitativa.objects.none(), required = False  )
    qo = forms.CharField( max_length = 120, required = False )

    def __init__(self, *args, **kwargs):
        self.itemsQualitativa = kwargs.pop('itemsQualitativa', None)
        super(qualitativaItemsForm,self).__init__(*args,**kwargs)
        self.fields['q1'].queryset = self.itemsQualitativa      
        self.fields['q2'].queryset = self.itemsQualitativa    
        self.fields['q3'].queryset = self.itemsQualitativa    
        #self.fields['q4'].queryset = self.itemsQualitativa      
        

#from alumnes.models import Alumne
class alumnesGrupForm(forms.Form):
    totElGrup = forms.BooleanField( required = False, help_text=u'''Tots els alumnes del grup''' )    
    alumnes = forms.ModelMultipleChoiceField( queryset= None, 
                                          required = False,
                                          help_text=u'''Pots triar o destriar més d'un alumne prement la tecla CTRL
                                                      mentre fas clic.
                                                      Per triar tots els alumnes selecciona el primer, 
                                                      baixa fins a l'últim i selecciona'l mantenint ara apretada
                                                      la tecla Shift ('Majúscules'),''')        

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', None)
        self.etiqueta = kwargs.pop('etiqueta', None)
        super(alumnesGrupForm,self).__init__(*args,**kwargs)
        self.fields['alumnes'].label = self.etiqueta 
        self.fields['totElGrup'].label = u'Tots els alumnes de ' + self.etiqueta 
        self.fields['alumnes'].queryset = self.queryset    
        
class triaQualitativaForm(forms.Form):
    qualitativa = forms.ModelChoiceField( queryset = AvaluacioQualitativa.objects.all(), required=True, help_text = u'Tria qualitativa')
    
    
                