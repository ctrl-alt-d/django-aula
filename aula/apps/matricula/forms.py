from django import forms
from captcha.fields import CaptchaField
from aula.apps.matricula.models import Peticio, Dades
from aula.apps.sortides.models import Quota, TipusQuota, QuotaPagament
from aula.apps.alumnes.models import Curs, Alumne
from aula.apps.extPreinscripcio.models import Preinscripcio
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
    
    def clean(self):
        cleaned_data = super(peticioForm, self).clean()
        idAlumne = cleaned_data.get('idAlumne').upper()
        tipus = cleaned_data.get('tipusIdent')
        if tipus=='R':
            # Comprova per RALC
            p=Preinscripcio.objects.filter(ralc=idAlumne)
        else:
            # Comprova per DNI
            p=Preinscripcio.objects.filter(identificador=idAlumne)
        if not p:
            raise forms.ValidationError("Identificador RALC o DNI erròni")
        self.instance.idAlumne = idAlumne
        cleaned_data['idAlumne'] = self.instance.idAlumne
        return cleaned_data  
        
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
    tipus_quota = forms.ModelChoiceField(label=u'Tipus de quota', queryset=None, required = True,)

    def __init__(self, *args, **kwargs):
        super(EscollirCursForm, self).__init__(*args, **kwargs)
        self.fields['curs_list'].queryset = Curs.objects.filter(grup__alumne__isnull=False, 
                                                                grup__alumne__data_baixa__isnull=True,
                                                ).order_by('nom_curs_complert').distinct()
        self.fields['tipus_quota'].queryset = TipusQuota.objects.filter(quota__isnull=False).order_by('nom').distinct()

class PagQuotesForm(forms.Form):
    pkp = forms.CharField( widget=forms.HiddenInput() )
    pka = forms.CharField( widget=forms.HiddenInput() )
    cognoms = forms.CharField( widget = forms.TextInput( attrs={'readonly': True} ), required=False, )
    nom = forms.CharField( widget = forms.TextInput( attrs={'readonly': True, 'style': 'width:100px'} ), required=False, )
    grup = forms.CharField(max_length=10, widget = forms.TextInput( attrs={'readonly': True, 'style': 'width:80px'} ) )
    correu = forms.CharField( widget = forms.TextInput( attrs={'readonly': True} ), required=False, )

    quota = ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=Quota.objects.all(),
            search_fields=('importQuota__icontains', 'descripcio__icontains',),
        ),
        queryset=Quota.objects.all(),
        required=False,
        )

    estat = forms.CharField(max_length=15, widget = forms.TextInput( attrs={'readonly': True, 'style': 'width:100px'} ) )
    fracciona = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        tipus = kwargs.pop('tipus')
        super(PagQuotesForm, self).__init__(*args, **kwargs)
        self.fields['quota'].widget.queryset=Quota.objects.filter(tipus=tipus).distinct()
        