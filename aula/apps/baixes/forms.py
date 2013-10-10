# This Python file uses the following encoding: utf-8
from django import forms
from aula.apps.usuaris.models import Professor
from django.utils.datetime_safe import datetime
from aula.utils.widgets import DateTextImput
    
class complementFormulariTriaForm( forms.Form):
    dia = forms.DateField(label=u'Data Baixa', 
                           initial=datetime.today(),
                           required = True, 
                           help_text=u'Data de la baixa',  
                           widget = DateTextImput() )
    professor = forms.ModelChoiceField( queryset=Professor.objects.all() )
    
    
class complementFormulariImpresioTriaForm( forms.Form):
    dia = forms.DateField(label=u'Data a Imprimir', 
                           initial=datetime.today(),
                           required = True, 
                           help_text=u'Dia a imprimir',  
                           widget = DateTextImput() )
    professors = forms.ModelMultipleChoiceField(  queryset=Professor.objects.all() )
    
        