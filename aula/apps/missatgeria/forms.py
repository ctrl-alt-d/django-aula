# This Python file uses the following encoding: utf-8

from django import forms as forms

class EmailForm(forms.Form):
    assumpte = forms.CharField(max_length=100)
    missatge = forms.CharField(widget=forms.Textarea)
    adjunts = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
