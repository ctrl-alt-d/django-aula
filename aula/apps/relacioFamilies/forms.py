import imghdr
from django import forms
from aula.apps.alumnes.models import Alumne
from aula.settings import CUSTOM_TIPUS_MIME_FOTOS


class AlumneModelForm(forms.ModelForm):
    class Meta:
        model = Alumne
        fields = ['correu_relacio_familia_pare', 'correu_relacio_familia_mare',
                  'periodicitat_faltes', 'periodicitat_incidencies', 'foto']

    def clean_foto(self):
            foto = self.cleaned_data['foto']
            if 'image/{0}'.format(imghdr.what(foto)) not in CUSTOM_TIPUS_MIME_FOTOS:
                message = "Tipus de fitxer no vàlid. Formats permesos: {0}".format(CUSTOM_TIPUS_MIME_FOTOS).replace("image/",'')
                raise forms.ValidationError(message)
            return foto
