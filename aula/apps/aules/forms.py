# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms as forms

from aula.apps.aules.models import Aula, ReservaAula
from aula.apps.horaris.models import FranjaHoraria
from django.forms.models import ModelChoiceField, ModelForm
from aula.django_select2.forms import ModelSelect2Widget
from django.utils.datetime_safe import datetime


from aula.utils.widgets import DateTextImput

class disponibilitatAulaPerAulaForm(forms.Form):

    aula = ModelChoiceField(
                   widget=ModelSelect2Widget(
                                        queryset=Aula.objects.filter(reservable = True),
                                        search_fields = ['nom_aula__icontains','descripcio_aula__icontains' ],
                                        attrs={'style':"'width': '100%'"},
                                        ),
                   queryset=Aula.objects.all(),
                   required=True,
                   help_text="Aula a consultar")

    data = forms.DateField(help_text="Data a consultar",
            initial=datetime.today(),
            required=True,
            widget=DateTextImput())


class disponibilitatAulaPerFranjaForm(forms.Form):

    franja = forms.ModelChoiceField( queryset = FranjaHoraria.objects.all()  )

    data = forms.DateField(help_text="Data a consultar",
                                initial=datetime.today(),
                                required=True,
                                widget=DateTextImput())

class AulesForm(forms.Form):
    aula = forms.ModelChoiceField( 
                        queryset = None,
                        empty_label=None
                                )

    def __init__(self, queryset, *args, **kwargs):
        super(AulesForm, self).__init__(*args, **kwargs)
        self.queryset = queryset
        self.fields['aula'].queryset = self.queryset



class reservaAulaForm(ModelForm):
    mou_alumnes= forms.ChoiceField(
                                label=u"És un canvi d'aula?",
                                help_text= """Pots fer un canvi d'aula o bé pots fer una nova reserva.
                                Canvi d'aula vol dir que deixes lliure la teva aula i portes els alumnes a l'aula que
                                estàs reservant.""",
                                initial="C",
                                required=True,
                                choices=[('C',u"Canvi d'aula"),('N','Nova reserva')],
                                widget=forms.RadioSelect())
    aula = ModelChoiceField(
                   widget=ModelSelect2Widget(
                                        queryset=Aula.objects.all(),
                                        search_fields = ['nom_aula__icontains','descripcio_aula__icontains' ],
                                        attrs={'style':"'width': '100%'"},
                                        ),
                   queryset=Aula.objects.all(),
                   required=True,
                   help_text="Aula a reservar")
                                
    class Meta:
        model = ReservaAula
        fields = ['aula','dia_reserva','hora','motiu']
        widgets = {
            'motiu': forms.Textarea,
            'dia_reserva' : DateTextImput()
        }


class carregaComentarisAulaForm(forms.Form):
    fitxerComentaris = forms.FileField(required=True)