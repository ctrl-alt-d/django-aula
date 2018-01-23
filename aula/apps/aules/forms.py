from django import forms as forms

from aula.apps.aules.models import Aula, ReservaAula
from django.forms.models import ModelChoiceField
from aula.django_select2.forms import ModelSelect2Widget
from django.utils.datetime_safe import datetime


from aula.utils.widgets import DateTextImput

class triaAulaSelect2Form(forms.Form):
    aula = ModelChoiceField(
                   widget=ModelSelect2Widget(
                                        queryset=Aula.objects.all(),
                                        search_fields = ['nom_aula__icontains', ],
                                        attrs={'style':"'width': '100%'"},
                                        ),
                   queryset=Aula.objects.all(),
                   required=True,
                   to_field_name="nom_aula",
                   help_text="Aula a consultar")




class disponibilitatAulaForm(forms.Form):

    data = forms.DateField(help_text="Data a consultar",
                                initial=datetime.today(),
                                required=True,
                                widget=DateTextImput())


    #
    # def __init__(self, *args, **kwargs):
    #     self.queryset = kwargs.pop('queryset', None)
    #     self.etiqueta = kwargs.pop('etiqueta', None)
    #     super(posaIncidenciaAulaForm, self).__init__(*args, **kwargs)
    #     self.fields['alumnes'].label = self.etiqueta
    #     self.fields['alumnes'].queryset = self.queryset
    #     self.totesLesFrases = FrassesIncidenciaAula.objects.all()
    #     incidencies = TipusIncidencia.objects
    #     self.fields['tipus'].queryset = incidencies.all()
    #     self.fields['tipus'].initial = incidencies.all()[0] if incidencies.exists() else None
    #







