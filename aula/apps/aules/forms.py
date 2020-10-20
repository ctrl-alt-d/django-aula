# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta
from django import forms as forms
from django.contrib.auth.models import User

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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(disponibilitatAulaPerFranjaForm, self).clean()

        data=self.cleaned_data['data']
        tretze_dies = timedelta(days=13)
        darrer_dia_reserva = datetime.today().date() + tretze_dies - timedelta(days=datetime.today().weekday())
        es_reservador = User.objects.filter(pk=self.user.pk, groups__name__in=['reservador']).exists()
        if not es_reservador and (data > darrer_dia_reserva or data < datetime.today().date()):
            raise forms.ValidationError(u"Només pots reservar a partir d'avui i fins al dia {0}".format(darrer_dia_reserva))

        franja = self.cleaned_data['franja']
        franges_del_dia = (FranjaHoraria
                           .objects
                           .filter(horari__impartir__dia_impartir=data)
                           .order_by('hora_inici')
                           )
        primera_franja = franges_del_dia.first()
        darrera_franja = franges_del_dia.last()
        if not primera_franja or franja.hora_inici < primera_franja.hora_inici or franja.hora_fi > darrera_franja.hora_fi:
            raise forms.ValidationError(u"En aquesta franja i dia no hi ha docència")

        return cleaned_data

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

    def clean_hora(self):

        franja = self.cleaned_data['hora']
        data = self.cleaned_data['dia_reserva']
        franges_del_dia = (FranjaHoraria
                           .objects
                           .filter(horari__impartir__dia_impartir=data)
                           .order_by('hora_inici')
                           )
        primera_franja = franges_del_dia.first()
        darrera_franja = franges_del_dia.last()
        if franja.hora_inici < primera_franja.hora_inici or franja.hora_fi > darrera_franja.hora_fi:
            raise forms.ValidationError(u"En aquesta franja i dia no hi ha docència")

        return franja

    class Meta:
        model = ReservaAula
        labels = {
            "motiu": "Propòsit"
        }
        fields = ['aula','dia_reserva','hora','motiu']
        widgets = {
            'motiu': forms.Textarea,
            'dia_reserva' : DateTextImput()
        }



class carregaComentarisAulaForm(forms.Form):
    fitxerComentaris = forms.FileField(required=True)