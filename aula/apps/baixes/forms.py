# This Python file uses the following encoding: utf-8
from django import forms
from aula.apps.usuaris.models import Professor
from django.utils.datetime_safe import datetime
    
class complementFormulariTriaForm( forms.Form):
    dia = forms.DateField(label=u'Data Baixa', 
                           initial=datetime.today(),
                           required = True, 
                           help_text=u'Data de la baixa',  
                           widget = forms.DateInput(attrs={'class':'datepicker'} ) )
    professor = forms.ModelChoiceField( queryset=Professor.objects.all() )
    
    
class complementFormulariImpresioTriaForm( forms.Form):
    dia = forms.DateField(label=u'Data a Imprimir', 
                           initial=datetime.today(),
                           required = True, 
                           help_text=u'Dia a imprimir',  
                           widget = forms.DateInput(attrs={'class':'datepicker'} ) )
    professors = forms.ModelMultipleChoiceField(  queryset=Professor.objects.all() )
    
        