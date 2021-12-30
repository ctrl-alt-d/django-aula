# This Python file uses the following encoding: utf-8
from django import forms
from aula.apps.usuaris.models import Professor
from django.utils.datetime_safe import datetime
from aula.utils.widgets import DateTextImput
from django.forms import  ModelChoiceField
from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget


class complementFormulariTriaForm( forms.Form):
    dia = forms.DateField(label=u'Data Baixa', 
                           initial=datetime.today(),
                           required = True, 
                           help_text=u'Data de la baixa',  
                           widget = DateTextImput() )
    professor = ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=Professor.objects.all(),
            search_fields=('last_name__icontains', 'first_name__icontains',),
            attrs={'style': "'width': '100%'"}
        ),
        queryset=Professor.objects.all(),
        required=True)
    
    
class complementFormulariImpresioTriaForm( forms.Form):
    dia = forms.DateField(label=u'Data a Imprimir', 
                           initial=datetime.today(),
                           required = True, 
                           help_text=u'Dia a imprimir',  
                           widget = DateTextImput() )
    professors = forms.ModelMultipleChoiceField(
                        label="Tria professors",
                        widget=ModelSelect2MultipleWidget(
                            queryset=Professor.objects.all(),
                            search_fields=('last_name__icontains', 'first_name__icontains',),
                            attrs={'style': "'width': '100%'"}
                            ),
                        queryset=Professor.objects.all(),
                        required=True)

