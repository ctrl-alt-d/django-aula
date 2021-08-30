# This Python file uses the following encoding: utf-8

from django import forms as forms

class sincronitzaEsferaForm(forms.Form):
    fitxerEsfera = forms.FileField(required=True)


class dadesAddicionalsForm(forms.Form):
    fitxerDadesAddicionals = forms.FileField(required=True)
