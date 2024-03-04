# This Python file uses the following encoding: utf-8
from django_select2.forms import ModelSelect2Widget
from aula.utils.widgets import DateTextImput
from django import forms as forms
from django.forms import ModelForm, RadioSelect, ModelChoiceField
from django.forms.widgets import DateInput, TextInput
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.presencia.models import ControlAssistencia  , EstatControlAssistencia
from aula.apps.usuaris.models import Professor
from datetime import datetime
from aula.apps.alumnes.models import Nivell, Grup
from aula.utils.widgets import bootStrapButtonSelect
from django.conf import settings

class ControlAssistenciaForm(ModelForm):
    from aula.utils.widgets import image
    
    foto = forms.ImageField(label='', required=False, widget=image(attrs={'readonly': True}))
    estat = forms.ModelChoiceField( 
                        label = "x",
                        #queryset= EstatControlAssistencia.objects.all(),
                        queryset = None,
                        empty_label=None,
                        widget = bootStrapButtonSelect( attrs={'class':'presenciaEstat'}, ),
                    )
    comunicat=forms.ModelChoiceField( label='', queryset = None, required=False )
    
    class Meta:
        model = ControlAssistencia
        fields = ('foto', 'estat', 'comunicat', )
        
    def __init__(self, *args, **kwargs):
        from aula.utils.widgets import modalButton
        from aula.apps.missatgeria.models import Missatge
        
        super(ControlAssistenciaForm, self).__init__(*args, **kwargs)
        self.fields['estat'].queryset = EstatControlAssistencia.objects.all()
        #self.fields['estat'].widget = bootStrapButtonSelect( attrs={'class':'presenciaEstat'}, ),
        if self.instance.comunicat:
            self.fields['comunicat'].initial=Missatge.objects.get(pk=self.instance.comunicat.id)
            self.fields['comunicat'].widget = modalButton(bname='Comunicat', info=self.instance.comunicat.text_missatge)
        else:
           self.fields['comunicat'].initial=None
           self.fields['comunicat'].widget = forms.HiddenInput()
        self.fields['foto'].initial=self.instance.alumne.foto

    def clean_comunicat(self):
        return self.instance.comunicat

class ControlAssistenciaFormFake(forms.Form):
    estat = forms.ChoiceField( required= False,  choices = [], widget = RadioSelect() )
    def is_valid(self):
        return True

#----------------------------------------------------------------

class afegeixGuardiaForm(forms.Form):
    professor = ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=Professor.objects.all(),
            search_fields=('last_name__icontains', 'first_name__icontains',),
            attrs={'style': "'width': '100%'"}
        ),
        queryset=Professor.objects.all(),
        required=True,
        help_text=u'Tria a quin professor fas la guardia.')
    franges = forms.ModelMultipleChoiceField( 
                        queryset= FranjaHoraria.objects.all(),
                        required= True,
                        help_text=u'Tria en quines franges horàries fas guardia.',
             )


#-------------------------------------------------------------------------------------------------------------
class regeneraImpartirForm(forms.Form):
    
    data_inici = forms.DateField(label=u'Data regeneració', 
                                       initial=datetime.today(),
                                       required = True, 
                                       help_text=u'Data en que entra en vigor l\'horari actual',  
                                       widget = DateTextImput() )
    
    franja_inici = forms.ModelChoiceField(queryset= FranjaHoraria.objects.all(), 
                                          required = True)
        
    confirma = forms.BooleanField( label=u'Confirma regenerar horaris',required = True,
                                   help_text=u'És un procés costos, confirma que el vols fer',  )
    
    def clean_data_regeneracio(self):
        data = self.cleaned_data['data_regeneracio']
        if data <  datetime.today():
            raise forms.ValidationError(u'Només es pot regenerar amb dates iguals o posteriors a avui.')

        # Always return the cleaned data, whether you have changed it or
        # not.
        return data

    
    def clean_confirma(self):
        data = self.cleaned_data['confirma']
        if not data:
            raise forms.ValidationError(u'Confirma la regeneració d\'horari.')

        return data
    

#---------------------------------------------------------------------------------------------------------------

#from alumnes.models import Alumne
class marcarComHoraSenseAlumnesForm(forms.Form):

    marcar_com_hora_sense_alumnes = forms.BooleanField(
                                                          required = False,
           help_text=u'''Marca aquesta opció si a aquesta hora no tens alumnes. (Per exemple optatives trimestrals)'''  )

    expandir_a_totes_les_meves_hores = forms.BooleanField(
                                                          required = False,
           help_text=u'''Marca aquesta opció per marcar a totes les classes que fas durant la setmana, no
                       només a aquesta classe.'''  )
    
#from alumnes.models import Alumne
class afegeixAlumnesLlistaExpandirForm(forms.Form):

    expandir_a_totes_les_meves_hores = forms.BooleanField(
                                                          required = False,
           help_text=u'''Marca aquesta opció per posar els alumnes a totes les classes que fas durant la setmana, no
                       només a aquesta classe. (Per exemple optatives)'''  )

    matmulla = forms.BooleanField(
                            label = u'''Moure l'alumne''',
                            help_text=u'''Marca aquesta opció treure l'alumne d'altres classes d'altres professors d'aquesta mateixa hora''',  
                            required = False,
                            initial = False
                            )

    
#from alumnes.models import Alumne
class afegeixTreuAlumnesLlistaForm(forms.Form):
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
        super(afegeixTreuAlumnesLlistaForm,self).__init__(*args,**kwargs)
        self.fields['alumnes'].label = self.etiqueta 
        self.fields['alumnes'].queryset = self.queryset



class calculadoraUnitatsFormativesForm(forms.Form):
    
    grup = forms.ModelChoiceField( queryset = None )
    assignatura = forms.ModelMultipleChoiceField( queryset = None )
    dataInici = forms.DateField(help_text=u'Data on començar a comptar', 
                                       initial= datetime.today(),
                                       required = True,                                          
                                       widget = DateTextImput() )
    hores = forms.IntegerField( help_text=u'Hores de la UF')    

    def __init__(self, *args, **kwargs):
        self.assignatures = kwargs.pop('assignatures', None)
        self.grups = kwargs.pop('grups', None)
        super(calculadoraUnitatsFormativesForm,self).__init__(*args,**kwargs)
        self.fields['assignatura'].queryset = self.assignatures 
        self.fields['grup'].queryset = self.grups


class faltesAssistenciaEntreDatesForm(forms.Form):
    
    grup = forms.ModelChoiceField( queryset = None )
    assignatura = forms.ModelMultipleChoiceField( queryset = None )
    dataDesDe = forms.DateField(help_text=u'Data on començar a comptar', 
                                       initial= datetime.today(),
                                       required = True,                                          
                                       widget = DateTextImput() )
    horaDesDe = forms.ModelChoiceField( queryset = None,
                                        initial = None)
    dataFinsA = forms.DateField(help_text=u'Data on començar a comptar', 
                                       initial= datetime.today(),
                                       required = True,                                          
                                       widget = DateTextImput() )
    horaFinsA = forms.ModelChoiceField( queryset = None,
                                        initial = None)

    def __init__(self, *args, **kwargs):
        self.assignatures = kwargs.pop('assignatures', None)
        self.grups = kwargs.pop('grups', None)
        super(faltesAssistenciaEntreDatesForm,self).__init__(*args,**kwargs)
        self.fields['assignatura'].queryset = self.assignatures 
        self.fields['grup'].queryset = self.grups
        self.fields['horaDesDe'].queryset = FranjaHoraria.objects.all()
        self.fields['horaDesDe'].initial = [FranjaHoraria.objects.all()[0]]
        self.fields['horaFinsA'].queryset = FranjaHoraria.objects.all()
        self.fields['horaFinsA'].initial = [  FranjaHoraria.objects.reverse()[0] ]


class alertaAssistenciaForm(forms.Form):
    data_inici = forms.DateField(label=u'Data inici', 
                                       initial=datetime.today(),
                                       required = True, 
                                       help_text=u'Dia inicial pel càlcul',  
                                       widget = DateTextImput() )
    
    data_fi = forms.DateField(label=u'Data fi', 
                                       initial=datetime.today(),
                                       required = True, 
                                       help_text=u'Dia final pel càlcul',  
                                       widget = DateTextImput() )
    
    tpc = forms.IntegerField( label = u'filtre %', 
                              max_value=100, 
                              min_value=1, initial = 25  ,
                              help_text=u'''Filtra alumnes amb % d'absència superior a aquest valor.''' ,
                              widget = TextInput(attrs={'class':"slider"} )  )
    
    nivell = forms.ModelChoiceField( 
                        queryset= Nivell.objects.all(), 
                        required = True, 
                        empty_label = None,
                    )    
    ordenacio = forms.ChoiceField(  choices = ( ('a', u'Nom alumne',), ('ca', u'Curs i alumne',),('n',u'Per % Assistència',), ('cn',u'Per Curs i % Assistència',), ), 
                                    required = True, 
                                    label = u'Ordenació', initial = 'a', help_text = u'Tria com vols ordenats els resultats')

    #toExcel = forms.BooleanField( u'Mostrar resultats en Full de Càlcul', help_text = u"Marcant aquesta casella els resultats no es mostren per pantalla, es decarregaran en un full de càlcul.")


#----------------------------------------------------------------------------------------------


class passaLlistaGrupDataForm( forms.Form ):
    grup = forms.ModelChoiceField( queryset = Grup.objects.filter(alumne__isnull = False).distinct().order_by("descripcio_grup")  )
    dia =  forms.DateField(label=u'Dia', 
                                       initial=datetime.today(),
                                       help_text=u'Dia a passar llista.',  
                                       widget = DateTextImput() )

  



class llistaLesMevesHoresForm( forms.Form ):
    hores = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1','1')), required=True)
    eliminarAlumnes = forms.BooleanField( label=u'Esborrar els alumnes actuals',required = False, initial=False,
            help_text=u'''Vull eliminar els alumnes que tinc en aquesta hora. \r\n 
            Compte no s'eliminaran els alumnes que tinguin assistències ja passades.\n
            ES UN PROCES MOOOLT LENT!!!''',  )

    def __init__(self, *args, **kwargs):
        self.llistaHoresProfe = kwargs.pop('llistaHoresProfe', None)
        super(llistaLesMevesHoresForm, self).__init__(*args, **kwargs)
        self.fields['hores'] = forms.ChoiceField(widget=forms.RadioSelect, choices=self.llistaHoresProfe, required=True)

#    Per fer validació extra.
#    def clean(self):
#        cleaned_data = super(llistaLesMevesHoresForm, self).clean()
#        hores = cleaned_data.get("hores")

