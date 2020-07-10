import imghdr
import io
import os

from PIL import Image
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile

from aula.apps.alumnes.models import Alumne
from aula.settings import CUSTOM_TIPUS_MIME_FOTOS


class AlumneModelForm(forms.ModelForm):

    class Meta:
        model = Alumne
        fields = ['primer_responsable','correu_relacio_familia_pare', 'correu_relacio_familia_mare',
                  'periodicitat_faltes', 'periodicitat_incidencies', 'foto', 'observacions']
        labels = {
            "correu_relacio_familia_pare": "Correu Notifi. Responsable 1",
            "correu_relacio_familia_mare": "Correu Notifi. Responsable 2",
        }
        help_texts = {
            "correu_relacio_familia_pare": "Correu notificació d'un responsable",
            "correu_relacio_familia_mare": "Correu notificació d'altre responsable(opcional)"
        }


    def __init__(self, *args, **kwargs):
        super(AlumneModelForm, self).__init__(*args, **kwargs)
        responsables = [self.instance.rp1_nom, self.instance.rp2_nom]
        responsable_choices = ((x, responsables[x]) for x in range(len(responsables)))
        self.fields['primer_responsable'] = forms.ChoiceField(choices=responsable_choices)
        self.fields['primer_responsable'].help_text = "Principal responsable de l'alumne/a"
        self.fields['primer_responsable'].label = "Reponsable preferent"

    def clean_foto(self):
        foto = self.cleaned_data['foto']
        if foto and 'image/{0}'.format(imghdr.what(foto)) not in CUSTOM_TIPUS_MIME_FOTOS:
            message = "Tipus de fitxer no vàlid. Formats permesos: {0}".format(CUSTOM_TIPUS_MIME_FOTOS).replace("image/",'')
            raise forms.ValidationError(message)
        return foto

    def save(self):
        #redimensionar i utilitzar ralc com a nom de foto
        try:
            img = Image.open(self.files['foto'])
            img.thumbnail((150, 150), Image.ANTIALIAS)
            thumb_io = io.BytesIO()
            img.save(thumb_io, self.files['foto'].content_type.split('/')[-1].upper())
            new_file_name ='alumne_' + str(self.instance.ralc) + os.path.splitext(self.instance.foto.name)[1]
            file = InMemoryUploadedFile(thumb_io,
                                        u"foto",
                                        new_file_name,
                                        self.files['foto'].content_type,
                                        thumb_io.getbuffer().nbytes,
                                        None)
            self.instance.foto = file
        except: pass
        super(AlumneModelForm, self).save()