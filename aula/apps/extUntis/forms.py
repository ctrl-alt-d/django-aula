from django import forms as forms

class sincronitzaUntisForm(forms.Form):
    fitxer_Untis = forms.FileField(required=True)
