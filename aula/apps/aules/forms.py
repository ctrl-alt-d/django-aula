from django import forms as forms

from aula.apps.aules.models import Aula, ReservaAula
from django.forms.models import ModelChoiceField, ModelForm
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
                   help_text="Aula a consultar")




class disponibilitatAulaForm(forms.Form):

    data = forms.DateField(help_text="Data a consultar",
                                initial=datetime.today(),
                                required=True,
                                widget=DateTextImput())


class reservaAulaForm(ModelForm):
     class Meta:
         model = ReservaAula
         fields = '__all__'
         widgets = {
             'motiu': forms.Textarea,
         }
         #exclude = ['usuari']

# class reservaAulaForm(forms.Form):
#
#     #aula = forms.CharField(max_length=100)
#
#
#     aula = forms.ModelChoiceField(queryset=Aula.objects.all(),
#                                    required=False,
#                                    help_text=u"""Aula a reservar""")
#     #
#     # dia = forms.DateField(datetime)
#     #
#     # hora = forms.ModelChoiceField(queryset=None,
#     #                               initial=None,
#     #                               empty_label=None)
#     #
#     #
#     motiu = forms.CharField(max_length=250, required=False,
#                             widget=forms.Textarea,
#                             help_text="No entrar dades personals, no entrar noms d'alumnes, no entrar noms de families")
#
#
#     #def __init__(self, *args, **kwargs):
#         #self.queryset = kwargs.pop('queryset', None)
#         #self.etiqueta = kwargs.pop('etiqueta', None)
#         #super(reservaAulaForm, self).__init__(*args, **kwargs)
#         #self.fields['alumnes'].label = self.etiqueta
#         #self.aula = self.aula
#         #self.totesLesFrases = FrassesIncidenciaAula.objects.all()
#         #incidencies = TipusIncidencia.objects
#         #self.fields['tipus'].queryset = incidencies.all()
#         #self.fields['tipus'].initial = incidencies.all()[0] if incidencies.exists() else None

