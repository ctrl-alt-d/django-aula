import datetime
from django import forms
from django.conf import settings
from django_select2.forms import ModelSelect2Widget
from django.forms.models import ModelChoiceField
from aula.apps.alumnes.models import Curs
from aula.apps.sortides.models import Sortida, Quota, QuotaPagament, TipusQuota, TPV
from django.core.exceptions import ValidationError

class PagamentForm(forms.Form):
    sortida = forms.CharField(widget=forms.HiddenInput())
    acceptar_condicions = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super(PagamentForm, self).__init__(*args, **kwargs)
        self.sortida = kwargs.pop('sortida', None)
        self.acceptar_condicions = False


class PagamentEfectiuForm(forms.Form):
    alumne = forms.CharField(disabled=True, label='Alumne/a', required=True, widget=forms.Textarea(attrs={'cols': 40, 'rows': 1}))
    sortida = forms.CharField(disabled=True, label='Activitat', widget=forms.Textarea(attrs={'cols': 40, 'rows': 1}), required=True)
    preu = forms.CharField(disabled=True, label='Preu(€)', required=True)
    data_hora_pagament = forms.CharField(label='Data/Hora pagament', required=True, widget=forms.DateInput(format="%Y-%m-%d %H:%M:%S"))
    ordre_pagament = forms.CharField(widget=forms.HiddenInput(), required=True)
    observacions = forms.CharField(widget=forms.TextInput())

    def clean_data_hora_pagament(self):
        data_hora = self.cleaned_data['data_hora_pagament']
        try:
            datetime.datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
        except:
            raise ValidationError('Format no correcte (Y-M-D H-M-S)')
        return data_hora

TIPUS_INIT = Sortida.TIPUS_PAGAMENT_CHOICES
TIPUS_CHOICES = []
if not settings.CUSTOM_SORTIDES_PAGAMENT_ONLINE:
    for c in TIPUS_INIT:
        if (c[0]!='ON'): TIPUS_CHOICES.append(c)
else:
    TIPUS_CHOICES = TIPUS_INIT
        
TIPUS_INIT = TIPUS_CHOICES
TIPUS_CHOICES = []
if not settings.CUSTOM_SORTIDES_PAGAMENT_CAIXER:
    for c in TIPUS_INIT:
        if (c[0]!='EB'): TIPUS_CHOICES.append(c)
else:
    TIPUS_CHOICES = TIPUS_INIT

class SortidaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SortidaForm, self).__init__(*args, **kwargs)
        self.fields['tipus_de_pagament'].choices = TIPUS_CHOICES

def year_choices():
    '''
    Retorna choices d'anys possibles per als pagaments
    '''
    primer=Quota.objects.all().order_by('any').first()
    ultim=Quota.objects.all().order_by('any').last()
    if bool(primer):
        primer=primer.any
    else:
        primer=current_year()
    if bool(ultim):
        ultim=ultim.any
    else:
        ultim=current_year()
    primerCurs=Curs.objects.filter(data_inici_curs__isnull=False).order_by('data_inici_curs').first()
    ultimCurs=Curs.objects.filter(data_fi_curs__isnull=False).order_by('data_fi_curs').last()
    if primerCurs and primerCurs.data_inici_curs.year<primer:
        primer = primerCurs.data_inici_curs.year
    if ultimCurs and ultimCurs.data_fi_curs.year>ultim:
        ultim = ultimCurs.data_fi_curs.year
    return [(r,r) for r in range(primer, ultim+1)]

def current_year():
    '''
    Retorna any de l'última quota registrada o any actual
    '''
    ultim=Quota.objects.all().order_by('any').last()
    if ultim:
        ultim = ultim.any
    else:
        ultim = datetime.date.today().year
    return ultim

class EscollirCursForm(forms.Form):
    '''
    Permet escollir curs, tipus de quota, any i si es fa assignació automàtica
    '''
    curs_list = forms.ModelChoiceField(label=u'Curs', queryset=None, required = True,)
    tipus_quota = forms.ModelChoiceField(label=u'Tipus de quota', queryset=None, required = True,)
    year = forms.TypedChoiceField(label='Any', coerce=int, choices=year_choices, initial=current_year, required = True)
    automatic = forms.BooleanField(label=u'Assigna automàticament', required = False)

    def __init__(self, user, *args, **kwargs):
        from django.contrib.auth.models import Group
        
        super(EscollirCursForm, self).__init__(*args, **kwargs)
        #Mostra cursos amb alumnes
        self.fields['curs_list'].queryset = Curs.objects.filter(grup__alumne__isnull=False, 
                                                                grup__alumne__data_baixa__isnull=True,
                                                ).order_by('nom_curs_complert').distinct()
        di=Group.objects.filter(name='direcció')
        ad=Group.objects.filter(name='administradors')
        if (di and di[0] not in user.groups.all()) and (ad and ad[0] not in user.groups.all()):
            # Si usuari no pertany a direcció ni administradors
            # només permet tipus de quotes que coincideixen amb l'usuari
            #  Exemple:  usuari ampa --> tipus de quota "ampa" 
            self.fields['tipus_quota'].queryset = TipusQuota.objects.exclude(nom='uf').exclude(nom='taxcurs').filter(quota__isnull=False, nom=user.username).order_by('nom').distinct()
        else:
            self.fields['tipus_quota'].queryset = TipusQuota.objects.exclude(nom='uf').exclude(nom='taxcurs').filter(quota__isnull=False).order_by('nom').distinct()

class PagQuotesForm(forms.Form):
    '''
    Mostra les quotes assignades als alumnes seleccionats
    '''
    pkp = forms.CharField( widget=forms.HiddenInput() )
    pka = forms.CharField( widget=forms.HiddenInput() )
    cognoms = forms.CharField( widget = forms.TextInput( attrs={'readonly': True} ), required=False, )
    nom = forms.CharField( widget = forms.TextInput( attrs={'readonly': True, 'style': 'width:100px'} ), required=False, )
    grup = forms.CharField(max_length=10, widget = forms.TextInput( attrs={'readonly': True, 'style': 'width:80px'} ) )
    correu = forms.CharField( widget = forms.TextInput( attrs={'readonly': True} ), required=False, )

    quota = ModelChoiceField(
        widget=ModelSelect2Widget(
            model=Quota,
            search_fields=('importQuota__icontains', 'descripcio__icontains',),
            attrs={'data-minimum-input-length':0},
        ),
        queryset=Quota.objects.all(),
        required=False,
        )

    estat = forms.CharField(max_length=15, widget = forms.TextInput( attrs={'readonly': True, 'style': 'width:100px'} ) )
    fracciona = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        tipus = kwargs.pop('tipus')
        nany = kwargs.pop('any')
        super(PagQuotesForm, self).__init__(*args, **kwargs)
        self.fields['quota'].widget.queryset=Quota.objects.filter(tipus=tipus, any=nany).distinct()

class EscollirTPV(forms.Form):
    '''
    Permet escollir el TPV i l'any per a la gestió de quotes
    Per defecte mostra el TPV reservat "centre", si l'usuari té permís.
    Depenent de l'usuari pot mostrar altres.
    '''
    defecte = TPV.objects.filter(nom='centre').first()
    tpv = forms.ModelChoiceField(label='TPV', queryset=None, initial=defecte, required = True,)
    year = forms.TypedChoiceField(label='Any', coerce=int, choices=year_choices, initial=current_year, required = True)
    
    def __init__(self, user, *args, **kwargs):
        from django.contrib.auth.models import Group
        
        super(EscollirTPV, self).__init__(*args, **kwargs)
        tp=Group.objects.get_or_create(name= 'tpvs' )
        if tp and tp[0] in user.groups.all():
            # Si l'usuari és del grup tpvs, només mostra el que correspon al seu nom
            #  Exemple:  usuari ampa --> TPV "ampa" 
            self.fields['tpv'].queryset = TPV.objects.filter(nom=user.username)
        else:
            self.fields['tpv'].queryset = TPV.objects.all()
