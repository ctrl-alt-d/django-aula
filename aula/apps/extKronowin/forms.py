from django import forms as forms
from django.forms import ModelForm

from aula.apps.extKronowin.models import Grup2Aula, Franja2Aula

#https://docs.djangoproject.com/en/1.2/topics/http/file-uploads/
class sincronitzaKronowinForm(forms.Form):
    fitxer_kronowin = forms.FileField(required=True)


class creaNivellCursGrupDesDeKronowinForm(forms.Form):
    fitxer_kronowin = forms.FileField(required=True)
    dia_inici_curs = forms.DateField()
    dia_fi_curs = forms.DateField()
    
class Kronowin2DjangoAulaGrupForm(ModelForm):

    
    class Meta:
        model = Grup2Aula
        fields = ('grup_kronowin', 'Grup2Aula' )
        widgets = {
            'grup_kronowin': forms.TextInput(attrs={'readonly': True}),
        }
    
        
class Kronowin2DjangoAulaFranjaForm(ModelForm):
    class Meta:
        model = Franja2Aula
        fields = ('franja_kronowin', 'franja_aula' )
        widgets = {
            'franja_kronowin': forms.TextInput(attrs={'readonly': True}),
        }            