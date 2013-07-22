# This Python file uses the following encoding: utf-8

from django import forms as forms

#https://docs.djangoproject.com/en/1.2/topics/http/file-uploads/
class sincronitzaSagaForm(forms.Form):
    fitxerSaga = forms.FileField(required=True)
