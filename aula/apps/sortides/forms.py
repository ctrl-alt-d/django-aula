from datetime import datetime
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from aula.apps.sortides.models import Sortida

class PagamentForm(forms.Form):
    sortida = forms.CharField(widget=forms.HiddenInput())
    check = forms.BooleanField(required=True, label="")
    Ds_MerchantParameters = forms.CharField(widget=forms.HiddenInput())
    Ds_Signature = forms.CharField(widget=forms.HiddenInput())
    acceptar_condicions = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super(PagamentForm, self).__init__(*args, **kwargs)
        self.sortida = kwargs.pop('sortida', None)
        self.Ds_MerchantParameters = kwargs.pop('Ds_MerchantParameters', None)
        self.Ds_Signature = kwargs.pop('signature', None)
        self.acceptar_condicions = kwargs.pop('signature', False)


class PagamentEfectiuForm(forms.Form):
    alumne = forms.CharField(disabled=True, label='Alumne/a', required=True, widget=forms.Textarea(attrs={'cols': 40, 'rows': 1}))
    sortida = forms.CharField(disabled=True, label='Activitat', widget=forms.Textarea(attrs={'cols': 40, 'rows': 1}), required=True)
    preu = forms.CharField(disabled=True, label='Preu(€)', required=True)
    data_hora_pagament = forms.CharField(label='Data/Hora pagament', required=True, widget=forms.DateInput(format="%Y-%m-%d %H:%M:%S"))
    ordre_pagament = forms.CharField(widget=forms.HiddenInput(), required=True)

    def clean_data_hora_pagament(self):
        data_hora = self.cleaned_data['data_hora_pagament']
        try:
            datetime.strptime(data_hora, "%Y-%m-%d %H:%M:%S")
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

