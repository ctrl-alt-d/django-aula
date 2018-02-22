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
