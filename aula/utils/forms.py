from aula.utils.widgets import DateTextImput

from django import forms
from django.forms.widgets import Widget

class ckbxForm(forms.Form):
    ckbx = forms.BooleanField(required = False  )
    
    def __init__(self, *args, **kwargs):
        self.label = kwargs.pop('label', None)
        self.help_text = kwargs.pop('help_text', None)
        self.defecte = kwargs.pop('defecte', False)
        super(ckbxForm,self).__init__(*args,**kwargs)
        self.fields['ckbx'].label = self.label 
        self.fields['ckbx'].help_text = self.help_text    
        self.fields['ckbx'].initial = self.defecte
        
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


def afegeigFormControlClass(unForm):
    for field in unForm.base_fields:
        unForm.base_fields[field].widget.attrs.update({'class': 'form-control'})


class initDBForm(forms.Form):
     
    confirma = forms.BooleanField( label=u'Confirma inicialització',required = True,
                                   help_text=u'Inicialitza la base de dades. Fa logout de tots els usuaris. Aquest procés no es pot desfer.\
                                               S\'hauria de realitzar abans una còpia de la base de dades.',  )
    
    def clean_confirma(self):
        data = self.cleaned_data['confirma']
        if not data:
            raise forms.ValidationError(u'Confirma la inicialització de la base de dades')

        return data
