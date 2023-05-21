# This Python file uses the following encoding: utf-8

from django import forms
from django.utils import version
from aula.utils.widgets import MultipleFileField, MultipleFileInput

class EmailForm(forms.Form):
    assumpte = forms.CharField(max_length=100)
    missatge = forms.CharField(widget=forms.Textarea)
    adjunts = MultipleFileField(required=False, widget=MultipleFileInput())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if version.get_main_version() <= '4.2':
            self.fields['adjunts'].widget=MultipleFileInput(attrs={'multiple': True})
        