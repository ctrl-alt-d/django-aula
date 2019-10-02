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
        fields = ['correu_relacio_familia_pare', 'correu_relacio_familia_mare',
                  'periodicitat_faltes', 'periodicitat_incidencies', 'foto']

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