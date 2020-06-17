# This Python file uses the following encoding: utf-8
from django import forms as forms
from aula.apps.alumnes.models import Grup

#-------------------------------------------------------------------------------------------------------------
class EscollirGrupForm(forms.Form):

    grup_list = forms.ModelChoiceField(label=u'Grup d\'alumnes', queryset=None, required = True,)
    nomesPropies = forms.BooleanField(label=u'Només hores pròpies', required = False)

    def __init__(self, professor, *args, **kwargs):
        super(EscollirGrupForm, self).__init__(*args, **kwargs)
        self.fields['grup_list'].queryset = Grup.objects.filter(horari__professor = professor).distinct()

    