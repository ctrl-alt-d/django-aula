# This Python file uses the following encoding: utf-8

from django import forms as forms
from aula.utils.widgets import SelectAjax, bootStrapButtonSelect
from django.forms import ModelForm

from aula.apps.alumnes.models import Nivell, Curs, Grup, Alumne
from aula.apps.usuaris.models import Professor

    
class triaAlumneForm(forms.Form):    
    #TODO: ha de suportar prefixos per si cal triar més d'un alumne    
    jquery_ajax = """
        var {busco}_done = function(res, status) {{
          if (status == "success") {{
              $("select#id_{busco}").html( res )
          }}
          else {{
            // display an explanation of failure
          }}
        }}
    
        var get_{busco} = function() {{
       
          var d = $("#id_{soc}").val()
          if (d != "" ) {{
            var args = {{ 
                type:"GET", 
                url:"/alumnes/triaAlumne{buscoCap}Ajax/"+d, 
                success:{busco}_done,
                error:function (xhr, ajaxOptions, thrownError){{
                        alert(xhr.status);
                        alert(thrownError);
                }}   
             }};
            $.ajax(args);
          }}
          else {{
            // display an explanation of failure
          }}
          return false;
        }};
    """
    
    jquery_nivell = jquery_ajax.format( soc='nivell', busco='curs', buscoCap='Curs' ) 
    jquery_curs = jquery_ajax.format(soc='curs',  busco='grup', buscoCap='Grup' ) 
    jquery_grup = jquery_ajax.format( soc='grup', busco='alumne', buscoCap='Alumne' ) 
    
    nivell = forms.ModelChoiceField( queryset = Nivell.objects.all(), required = False,
                                     widget =  SelectAjax( jquery=jquery_nivell,  
                                                           buit=False,attrs={'onchange':'get_curs();'} ) )
    
    curs = forms.ModelChoiceField( queryset = Curs.objects.all(),required = False,
                                     widget =  SelectAjax( jquery=jquery_curs, 
                                                           buit=True, attrs={'onchange':'get_grup();'} ) )
    
    grup = forms.ModelChoiceField( queryset = Grup.objects.all(), required = False,
                                     widget =  SelectAjax( jquery=jquery_grup , 
                                                           buit=True, attrs={'onchange':'get_alumne();'} ) )

    alumne = forms.ModelChoiceField( queryset = Alumne.objects.all(),
                                     widget =  SelectAjax( buit=True ) )
    
#---form assignar grup -----------------------------------------------------------------------------------------
class grupForm(ModelForm):
    class Meta:
        model = Grup
        fields = ('curs', 'nom_grup' )            

#---form assignar tutor-----------------------------------------------------------------------------------------
class tutorsForm(forms.Form):  
    grup = forms.CharField( widget = forms.TextInput( attrs={'readonly': True} ) ) 
    tutor1 = forms.ModelChoiceField( queryset = Professor.objects.all(), required = False  )
    tutor2 = forms.ModelChoiceField( queryset = Professor.objects.all(), required = False  )
    tutor3 = forms.ModelChoiceField( queryset = Professor.objects.all(), required = False  )
    
    
#--tutoria individualitzada:
#from alumnes.models import Alumne
class triaMultiplesAlumnesForm(forms.Form):
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
        super(triaMultiplesAlumnesForm,self).__init__(*args,**kwargs)
        self.fields['alumnes'].label = self.etiqueta 
        self.fields['alumnes'].queryset = self.queryset

# ---------------- PROMOCIONS ------------------------#

__author__ = 'David'
CHOICES = (
    ('0','MOU'),
    ('1','IGUAL'),
    ('2','MARXA'),

)
class promoForm(ModelForm):
    decisio = forms.ChoiceField(widget=bootStrapButtonSelect(attrs={'class': 'buttons-promos disabled', }),choices=CHOICES,)
    class Meta:
        model = Alumne
        fields  = []

class newAlumne(ModelForm):
    class Meta:
        model = Alumne
        fields = ['grup', 'nom', 'cognoms', 'data_neixement', 'correu_tutors', 'correu_relacio_familia_pare', 'correu_relacio_familia_mare', 'tutors_volen_rebre_correu', 'centre_de_procedencia', 'localitat', 'telefons', 'tutors', 'adreca']




           
    
