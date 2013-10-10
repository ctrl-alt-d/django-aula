from aula.utils.widgets import DateTextImput

from django import forms
from django.forms.widgets import Widget

class ckbxForm(forms.Form):
    ckbx = forms.BooleanField(required = False  )
    
    def __init__(self, *args, **kwargs):
        self.label = kwargs.pop('label', None)
        self.help_text = kwargs.pop('help_text', None)
        super(ckbxForm,self).__init__(*args,**kwargs)
        self.fields['ckbx'].label = self.label 
        self.fields['ckbx'].help_text = self.help_text    
        
class dataForm(forms.Form):
    data = forms.DateField( required = False ,
                            widget = DateTextImput() )
    
    def __init__(self, *args, **kwargs):
        self.label = kwargs.pop('label', None)
        self.help_text = kwargs.pop('help_text', None)
        super(dataForm,self).__init__(*args,**kwargs)
        self.fields['data'].label = self.label 
        self.fields['data'].help_text = self.help_text    

class hiddenIntForm(forms.Form):
    enter = forms.IntegerField( widget = forms.HiddenInput() )
    
    def __init__(self, *args, **kwargs):
        self.initial = kwargs.pop('initial', None)
        super(hiddenIntForm,self).__init__(*args,**kwargs)
        self.fields['enter'].initial = self.initial    


class choiceForm(forms.Form):
    opcio  = forms.ChoiceField(  widget = forms.RadioSelect  )

    def __init__(self, *args, **kwargs):
        self.label = kwargs.pop('label', None)
        self.help_text = kwargs.pop('help_text', None)        
        self.opcions = kwargs.pop('opcions', None)        
        super(choiceForm,self).__init__(*args,**kwargs)
        self.fields['opcio'].choices = self.opcions
        self.fields['opcio'].label = self.label 
        self.fields['opcio'].help_text = self.help_text          
        
        


        
                