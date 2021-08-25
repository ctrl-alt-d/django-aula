from django import forms as forms

class PreinscripcioForm(forms.Form):
    fitxer_Preinscripcio = forms.FileField(required=True, label="Fitxer de la preinscripció")
