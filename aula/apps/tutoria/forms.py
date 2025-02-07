# This Python file uses the following encoding: utf-8
from aula.utils.widgets import DateTextImput

from django import forms as forms
import datetime
from aula.apps.alumnes.models import Alumne, Grup, AlumneGrup
from django.forms.widgets import Widget
from django_select2.forms import ModelSelect2Widget

class elsMeusAlumnesTutoratsEntreDatesForm( forms.Form ):
    grup = forms.ChoiceField(  help_text=u'Tria un grup per veure dades del grup.')
    dataDesDe =  forms.DateField(label=u'Data des de', 
                                       initial=datetime.date.today,
                                       required = False, 
                                       help_text=u'Rang de dates: primer dia.',  
                                       widget = DateTextImput() )

    dataFinsA =  forms.DateField(label=u'Data fins a', 
                                       initial=datetime.date.today,
                                       required = True, 
                                       help_text=u'Rang de dates: darrer dia.',  
                                       widget = DateTextImput() )



    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('grups', None)
        super(elsMeusAlumnesTutoratsEntreDatesForm,self).__init__(*args,**kwargs)
        self.fields['grup'].choices = self.queryset    
                

class justificaFaltesW1Form(forms.Form):
    from django.forms.models import ModelChoiceField
    
    alumne = ModelChoiceField( 
                widget=ModelSelect2Widget(
                                     queryset=AlumneGrup.objects.none(),
                                     search_fields = [
                                         'cognoms__icontains',
                                         'nom__icontains',
                                         'nom_sentit__icontains',
                                         'grup__descripcio_grup__icontains'
                                         ],
                                     attrs={'style':"'width': '100%'",
                                            'data-placeholder': "(Justificador)"},
                                     ),        
                queryset= AlumneGrup.objects.all(),
                required = False, 
                help_text=u"""Alumne al que vols justificar faltes.(Justificador per tot el grup)"""  )

    data = forms.DateField(label=u'Data faltes a justificar', 
                                       initial=datetime.date.today,
                                       required = True, 
                                       help_text=u'Data on hi ha les faltes a justificar.',  
                                       widget = DateTextImput() )

    pas = forms.IntegerField(  initial=1, widget = forms.HiddenInput() )

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', None)
        super(justificaFaltesW1Form,self).__init__(*args,**kwargs)
        self.fields['alumne'].widget.queryset = self.queryset
        
class informeSetmanalForm(forms.Form):
    grup = forms.ModelChoiceField( queryset= Grup.objects.none(), 
                                          required = False, 
                                          empty_label="-- Tots els alumnes --",
                                          help_text=u"""Tria un grup per fer l'informe."""  )

    data = forms.DateField(label=u'Setmana informe:', 
                                       initial=datetime.date.today,
                                       required = True, 
                                       help_text=u'Data on hi ha les faltes a justificar.',  
                                       widget = DateTextImput() )

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop('queryset', None)
        super(informeSetmanalForm,self).__init__(*args,**kwargs)
        self.fields['grup'].queryset = self.queryset
        
class seguimentTutorialForm(forms.Form):
    pregunta_oberta  = forms.CharField(  )
    pregunta_select  = forms.ChoiceField(  widget = forms.RadioSelect  )

    def __init__(self, *args, **kwargs):
        self.pregunta = kwargs.pop('pregunta', None)
        self.resposta_anterior = kwargs.pop('resposta_anterior', None)
        self.alumne = kwargs.pop('alumne', None)
        self.tutor = kwargs.pop('tutor', None)    

        super(seguimentTutorialForm,self).__init__(*args,**kwargs)
        if self.pregunta.es_pregunta_oberta:
            del self.fields['pregunta_select']
            self.q_valida = 'pregunta_oberta'
            self.fields[self.q_valida].widget.attrs={'size':'40'} 
        else:
            del self.fields['pregunta_oberta']
            self.q_valida = 'pregunta_select'
            self.fields['pregunta_select'].choices= [ (x.strip(),x.strip(), ) for x in self.pregunta.possibles_respostes.split('|')]  #[('',u'---Tria---')] +
        self.fields[self.q_valida].initial=self.resposta_anterior.resposta.strip() if self.resposta_anterior else None
        self.fields[self.q_valida].label = u'{0}'.format( self.pregunta.pregunta)
        self.fields[self.q_valida].help_text = self.pregunta.ajuda_pregunta   
        self.fields[self.q_valida].required = True 
        if self.pregunta.pregunta == 'Tutor/a' and self.q_valida == 'pregunta_oberta' and not self.fields[self.q_valida].initial:
            self.fields[self.q_valida].initial = u"{0}".format( self.tutor )
        if self.pregunta.pregunta == 'Curs' and self.q_valida == 'pregunta_oberta' and not self.fields[self.q_valida].initial:
            self.fields[self.q_valida].initial = u"{0}".format( self.alumne.grup )

        
 




                        