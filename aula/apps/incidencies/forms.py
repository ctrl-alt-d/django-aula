# This Python file uses the following encoding: utf-8

from django import forms as forms

from aula.apps.incidencies.models import FrassesIncidenciaAula, Expulsio
from aula.apps.incidencies.models import TipusIncidencia
from aula.apps.usuaris.models import Professor
from django_select2.forms import ModelSelect2Widget
from aula.utils.widgets import DateTextImput

class incidenciesRelacionadesForm(forms.Form):
    incidenciesRelacionades = forms.ModelMultipleChoiceField( 
                                                      label = u"Incidencies Relacionades",
                                                      queryset = None,
                                                      required = False,
                                                      widget=forms.CheckboxSelectMultiple,
                                                      help_text = u"Tria les incidències relacionades amb aquesta expulsió.")

    expulsionsRelacionades = forms.ModelMultipleChoiceField( 
                                                      label = u"Expulsions Relacionades",
                                                      queryset = None,
                                                      required = False,
                                                      widget=forms.CheckboxSelectMultiple,
                                                      help_text = u"Tria les expulsions relacionades amb aquesta expulsió.")
    
    def __init__(self, *args, **kwargs):
        self.querysetIncidencies = kwargs.pop('querysetIncidencies', None)
        self.querysetExpulsions = kwargs.pop('querysetExpulsions', None)
        super(incidenciesRelacionadesForm,self).__init__(*args,**kwargs)
        self.fields['incidenciesRelacionades'].queryset = self.querysetIncidencies 
        self.fields['expulsionsRelacionades'].queryset = self.querysetExpulsions
        self.fields['incidenciesRelacionades'].initial = self.querysetIncidencies 
        self.fields['expulsionsRelacionades'].initial = self.querysetExpulsions

#from alumnes.models import Alumne
class posaIncidenciaAulaForm(forms.Form):
    
    alumnes = forms.ModelMultipleChoiceField( queryset= None, 
                                          required = False, 
                                          help_text=u"""Alumne(s) al(s) que posaràs incidència(es). 
                                              Pots triar-ne més d'un. Per triar més d'un alumne has 
                                              de mantenir pulsada la tecla CTRL al fer
                                              clic amb el ratolí."""  )

    tipus = forms.ModelChoiceField( queryset = None,
                                    empty_label=None,
                                    initial = None,
                                    widget=forms.RadioSelect(attrs={"onChange":'getFrase()'})
                                   )

    frases = forms.ModelMultipleChoiceField( label=u'Tria incidència', queryset= FrassesIncidenciaAula.objects.all(), 
                                          required = False,
                                          help_text=u"""Frase de la incidència. 
                                              En pots triar més d'una, i es generaran tantes incidències com frases triis.
                                              Per triar més d'una frase has de mantenir pulsada la tecla CTRL al fer
                                              clic amb el ratolí."""  )

    
    frase = forms.CharField( label=u'o bé escriu incidència', max_length = 350, required=False,
                            widget=forms.Textarea,
                             help_text=u"""Pots escriure tu mateix la frase de la incidència en cas que no aparegui a les 
                                         frases predefinides. 
                                        Aquesta informació la veuen els pares i els professors que imparteixen docència a aquest alumne.
                                        Atenció: Pots escriure i triar frase a la vegada: es crearan dues incidències.
                                        """  )


    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', None)
        self.etiqueta = kwargs.pop('etiqueta', None)
        super(posaIncidenciaAulaForm,self).__init__(*args,**kwargs)
        self.fields['alumnes'].label = self.etiqueta 
        self.fields['alumnes'].queryset = self.queryset
        self.totesLesFrases = FrassesIncidenciaAula.objects.all()
        incidencies = TipusIncidencia.objects
        self.fields['tipus'].queryset = incidencies.all()
        self.fields['tipus'].initial = incidencies.all()[0] if incidencies.exists() else None

    
    
#-------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------

#TODO: Canviar per una factoria --------------------------------------------------------<
class posaExpulsioForm(forms.ModelForm):
    class Meta:
        model = Expulsio
        fields = ( 'dia_expulsio', 'franja_expulsio'  )
        widgets = {
                   'dia_expulsio': DateTextImput() 
                   }

#TODO: Canviar per una factoria --------------------------------------------------------<
class posaExpulsioFormW2(forms.ModelForm):
    
    class Meta:
        model = Expulsio
        fields = ( 'professor', )
        widgets = {
            'professor':ModelSelect2Widget(
                            queryset=Professor.objects.all(),
                            search_fields=('last_name__icontains', 'first_name__icontains',),
                            attrs={'style': "'width': '100%'"}
                        )
        }
                    
    


        