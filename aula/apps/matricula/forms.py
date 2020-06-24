from django import forms
from captcha.fields import CaptchaField
from aula.apps.matricula.models import Peticio, Dades
from aula.apps.sortides.models import Quota
from aula.apps.alumnes.models import Curs, Alumne
from aula.utils.widgets import DateTextImput
from aula.django_select2.forms import ModelSelect2Widget
from django.forms.models import ModelChoiceField

class peticioForm(forms.ModelForm):
    '''
    Formulari petició de Matrícula
    Demana un captcha per evitar accesos automàtics, configurat al settings.
    '''
    
    captcha = CaptchaField(label="")

    class Meta:
        model = Peticio
        fields = ['idAlumne','tipusIdent','email','curs']
        
    def __init__(self, *args, **kwargs):
        super(peticioForm, self).__init__(*args, **kwargs)
        self.fields['curs'].queryset = Curs.objects.filter(nivell__matricula_oberta=True).order_by('nom_curs_complert')
        
class DadesForm1(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DadesForm1, self).__init__(*args, **kwargs)
        self.fields['data_naixement'].widget=DateTextImput()
        
    class Meta:
        model=Dades
        fields = ['nom','cognoms','centre_de_procedencia','data_naixement','alumne_correu','adreca','localitat','cp',]

class DadesForm2(forms.ModelForm):
    
    class Meta:
        model=Dades
        fields = ['rp1_nom','rp1_telefon1','rp1_correu','rp2_nom','rp2_telefon1','rp2_correu',]

class DadesForm3(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(DadesForm3, self).__init__(*args, **kwargs)
        self.fields['acceptar_condicions'].required=True
    
    class Meta:
        model=Dades
        fields = ['files','acceptar_condicions',]

class MatriculaForm(forms.ModelForm):
    
    class Meta:
        model = Dades
        fields = ['nom','cognoms','acceptar_condicions','files',]

class EscollirCursForm(forms.Form):

    curs_list = forms.ModelChoiceField(label=u'Curs', queryset=None, required = True,)

    def __init__(self, *args, **kwargs):
        super(EscollirCursForm, self).__init__(*args, **kwargs)
        self.fields['curs_list'].queryset = Curs.objects.filter(grup__alumne__isnull=False, grup__alumne__data_baixa__isnull=True).distinct()

class PagQuotesForm(forms.Form):
    cognoms = forms.CharField( widget = forms.TextInput( attrs={'readonly': True} ) )
    nom = forms.CharField( widget = forms.TextInput( attrs={'readonly': True, 'style': 'width:100px'} ) )
    grup = forms.CharField(max_length=10, widget = forms.TextInput( attrs={'readonly': True, 'style': 'width:80px'} ) )
    correu = forms.CharField( widget = forms.TextInput( attrs={'readonly': True} ) )

    quota = ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=Quota.objects.all(),
            search_fields=('importQuota__icontains', 'descripcio__icontains',),
        ),
        queryset=Quota.objects.all(),
        required=False,
        )

    pagament = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    estat = forms.CharField(max_length=15, widget = forms.TextInput( attrs={'readonly': True, 'style': 'width:100px'} ) )
    '''
    def __init__(self, *args, **kwargs):
        super(PagQuotesForm, self).__init__(*args, **kwargs)
        self.fields['quota'].disabled=kwargs['initial']['pagament'] if 'initial' in kwargs else False
    '''
    