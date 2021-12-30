# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import timedelta
from django import forms as forms
from django.contrib.auth.models import User

from aula.apps.material.models import Recurs, ReservaRecurs
from aula.apps.horaris.models import FranjaHoraria
from django.forms.models import ModelChoiceField, ModelForm

from aula.apps.usuaris.forms import triaProfessorSelect2Form
from aula.apps.usuaris.models import Professor
from django_select2.forms import ModelSelect2Widget
from django.utils.datetime_safe import datetime
from aula.utils.widgets import DateTextImput

class disponibilitatRecursPerRecursForm(forms.Form):

    recurs = ModelChoiceField(
                   widget=ModelSelect2Widget(
                                        queryset=Recurs.objects.filter(reservable = True),
                                        search_fields = ['nom_recurs__icontains','descripcio_recurs__icontains' ],
                                        attrs={'style':"'width': '100%'",
                                               'data-minimum-input-length':0},
                                        ),
                   queryset=Recurs.objects.all(),
                   required=True,
                   help_text="Material a consultar")

    data = forms.DateField(help_text="Data a consultar",
            initial=datetime.today(),
            required=True,
            widget=DateTextImput())


class disponibilitatRecursPerFranjaForm(forms.Form):

    franja = forms.ModelChoiceField( queryset = FranjaHoraria.objects.all()  )

    data = forms.DateField(help_text="Data a consultar",
                                initial=datetime.today(),
                                required=True,
                                widget=DateTextImput())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(disponibilitatRecursPerFranjaForm, self).clean()

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
        if not franja or not primera_franja or not darrera_franja or (franja.hora_inici < primera_franja.hora_inici or franja.hora_fi > darrera_franja.hora_fi):
            raise forms.ValidationError(u"En aquesta franja i dia no hi ha docència")

        return cleaned_data

class RecursosForm(forms.Form):
    recurs = forms.ModelChoiceField(
                        queryset = None,
                        empty_label=None
                                )

    def __init__(self, queryset, *args, **kwargs):
        super(RecursosForm, self).__init__(*args, **kwargs)
        self.queryset = queryset
        self.fields['recurs'].queryset = self.queryset



class reservaRecursForm(ModelForm):
    recurs = ModelChoiceField(
                   widget=ModelSelect2Widget(
                                        queryset=Recurs.objects.all(),
                                        search_fields = ['nom_recurs__icontains','descripcio_recurs__icontains' ],
                                        attrs={'style':"'width': '100%'",
                                               'data-minimum-input-length':0},
                                        ),
                   queryset=Recurs.objects.all(),
                   required=True,
                   help_text="Material a reservar")

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
        model = ReservaRecurs
        labels = {
            "motiu": "Propòsit"
        }
        fields = ['recurs','dia_reserva','hora','motiu']
        widgets = {
            'motiu': forms.Textarea,
            'dia_reserva' : DateTextImput()
        }



class carregaComentarisRecursForm(forms.Form):
    fitxerComentaris = forms.FileField(required=True)


class disponibilitatMassivaRecursPerFranjaForm(forms.Form):

    franja = forms.ModelChoiceField( queryset = FranjaHoraria.objects.all()  )

    data_inici = forms.DateField(help_text="Data d'inici a consultar",
                                 initial=datetime.today(),
                                 required=True,
                                 widget=DateTextImput())

    data_fi = forms.DateField(help_text="Data de fi a consultar",
                                 initial=datetime.today(),
                                 required=True,
                                 widget=DateTextImput())

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(disponibilitatMassivaRecursPerFranjaForm, self).clean()

        data_inici=self.cleaned_data['data_inici']
        data_fi = self.cleaned_data['data_fi']
        dia_setmana_data_inici = data_inici.weekday()
        dia_setmana_data_fi = data_fi.weekday()
        if dia_setmana_data_inici != dia_setmana_data_fi:
            raise forms.ValidationError(u"Les dates d'inici i fi no coincideixen en el dia de la setmana (dilluns, dimarts,...)")
        es_reservador = User.objects.filter(pk=self.user.pk, groups__name__in=['reservador']).exists()
        if not es_reservador:
            raise forms.ValidationError(u"Aquesta acció només la pot realitzar un usuari amb permissos")

        franja = self.cleaned_data['franja']
        franges_del_dia = (FranjaHoraria
                           .objects
                           .filter(horari__impartir__dia_impartir=data_inici)
                           .order_by('hora_inici')
                           )
        primera_franja = franges_del_dia.first()
        darrera_franja = franges_del_dia.last()
        if dia_setmana_data_inici in [5,6] or franja.hora_inici < primera_franja.hora_inici or franja.hora_fi > darrera_franja.hora_fi:
            raise forms.ValidationError(u"En aquesta franja i dia no hi ha docència")

        return cleaned_data


class reservaMassivaRecursForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(reservaMassivaRecursForm, self).__init__(*args, **kwargs)
        self.fields['hora'].disabled = True
        self.fields['recurs'].disabled = True
        self.fields["usuari"].queryset = Professor.objects.all()

    recurs = ModelChoiceField(
                   widget=ModelSelect2Widget(
                                        queryset=Recurs.objects.all(),
                                        search_fields = ['nom_recurs__icontains','descripcio_recurs__icontains' ],
                                        attrs={'style':"'width': '100%'",
                                               'data-minimum-input-length':0},
                                        ),
                   queryset=Recurs.objects.all(),
                   required=True,
                   help_text="Material a reservar",)

    usuari = triaProfessorSelect2Form()

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
        model = ReservaRecurs
        labels = {
            "motiu": "Propòsit"
        }
        fields = ['recurs', 'dia_reserva', 'hora', 'motiu', 'usuari']
        widgets = {
            'motiu': forms.Textarea,
            'dia_reserva': forms.HiddenInput
        }
