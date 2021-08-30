import imghdr
import io
import os

from PIL import Image
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile

from aula.apps.alumnes.models import Alumne
from aula.settings import CUSTOM_TIPUS_MIME_FOTOS

def tipusFotoOK(foto):
    if foto and 'image/{0}'.format(imghdr.what(foto)) not in CUSTOM_TIPUS_MIME_FOTOS:
        message = "Tipus de fitxer no vàlid. Formats permesos: {0}".format(CUSTOM_TIPUS_MIME_FOTOS).replace("image/",'')
        return False, message
    return True, None
        
def convertirFoto(fitxer, ralc, foto):
    img = Image.open(fitxer)
    img.thumbnail((150, 150), Image.ANTIALIAS)
    thumb_io = io.BytesIO()
    img.save(thumb_io, fitxer.content_type.split('/')[-1].upper())
    new_file_name ='alumne_' + str(ralc) + os.path.splitext(foto.name)[1]
    file = InMemoryUploadedFile(thumb_io,
                                u"foto",
                                new_file_name,
                                fitxer.content_type,
                                thumb_io.getbuffer().nbytes,
                                None)
    return file

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
        self.fields['primer_responsable'].label = "Responsable preferent"

    def clean_foto(self):
        foto = self.cleaned_data['foto']
        ok, mess = tipusFotoOK(foto)
        if not ok:
            raise forms.ValidationError(mess)
        return foto

    def save(self):
        #redimensionar i utilitzar ralc com a nom de foto
        try:
            self.instance.foto = convertirFoto(self.files['foto'], self.instance.ralc, self.instance.foto)
        except: pass
        super(AlumneModelForm, self).save()