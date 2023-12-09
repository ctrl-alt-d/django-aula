import imghdr
import io
import os

from PIL import Image
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile

from aula.apps.alumnes.models import Alumne
from aula.settings import CUSTOM_TIPUS_MIME_FOTOS
from aula.utils.widgets import SelectAjax, DataHoresAlumneAjax

def tipusFotoOK(foto):
    if foto and 'image/{0}'.format(imghdr.what(foto)) not in CUSTOM_TIPUS_MIME_FOTOS:
        message = "Tipus de fitxer no vàlid. Formats permesos: {0}".format(CUSTOM_TIPUS_MIME_FOTOS).replace("image/",'')
        return False, message
    return True, None
        
def convertirFoto(fitxer, ralc, foto):
    img = Image.open(fitxer)
    img.thumbnail((500, 500), Image.Resampling.LANCZOS)
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

class ChoiceFieldNoValidation(forms.ChoiceField):
    def validate(self, value):
        pass

class comunicatForm(forms.Form):
    MOTIUS = [
        ('M', 'Malaltia'),
        ('V', 'Visita mèdica'),
        ('F', 'Motius familiars'),
        ('L', 'Motius laborals'),
        ('T', 'Problemes transport'),
        ('A', 'Altres'),
        ]
    
    datainici = forms.DateField(label='des de data', required=True)
    horainici = ChoiceFieldNoValidation(label='primera hora', required=False)
    datafi = forms.DateField(label='fins data', required=False)
    horafi = ChoiceFieldNoValidation(label='última hora', required=False)
    motiu = forms.ChoiceField(label='motiu', required=False, choices=MOTIUS)
    observacions = forms.CharField(label='observacions', widget=forms.Textarea, required=False,
                                   help_text='obligatori si motiu "Altres".')
    
    def __init__(self, alumne, primerdia, ultimdia, *args, **kwargs):
        import datetime

        super().__init__(*args, **kwargs)
        if not alumne: return
        pdia=primerdia
        udia=ultimdia
        if self.is_bound and self.data:
            datai=self.data['datainici']
            #Modifica límits per al segon widget
            pdia=datetime.datetime.strptime(datai, '%d/%m/%Y').date()
        self.fields['datainici'].widget = DataHoresAlumneAjax(id_selhores='horainici', almnid=alumne.id, id_dt_end='datafi', pd=primerdia, ud=ultimdia)
        self.fields['datafi'].widget = DataHoresAlumneAjax(id_selhores='horafi', almnid=alumne.id, pd=pdia, ud=udia)

    def clean(self):
        from aula.apps.horaris.models import FranjaHoraria
        cleaned_data = super().clean()
        datai=cleaned_data.get('datainici')
        dataf=cleaned_data.get('datafi')
        horai=cleaned_data.get('horainici')
        horaf=cleaned_data.get('horafi')
        motiu=cleaned_data.get('motiu')
        observ=cleaned_data.get('observacions')
        if not bool(dataf):
            dataf=datai
            cleaned_data['datafi'] = dataf
            if bool(horai):
                horaf=horai
                cleaned_data['horafi'] = horaf
        if dataf<datai:
            self.add_error('datafi','data final no pot ser anterior a la inicial')
            return cleaned_data
        
        if bool(horai) and horai!="0":
            franjai=FranjaHoraria.objects.get(id=horai) 
        else:
            horai="0"
            cleaned_data['horainici'] = horai
            franjai=None
        if bool(horaf) and horaf!="0":
            franjaf=FranjaHoraria.objects.get(id=horaf) 
        else:
            horaf="0"
            cleaned_data['horafi'] = horaf
            franjaf=None
        if dataf==datai and horai!=horaf and franjai and franjaf and franjaf.hora_inici<franjai.hora_inici:
            self.add_error('horafi','hora final no pot ser anterior a la inicial')
            return cleaned_data
        if dataf==datai and horai!=horaf and not franjai:
            self.add_error('horafi','Si dia complet no fa falta hora fi')
            return cleaned_data
        if dataf==datai and horai!=horaf and not franjaf:
            self.add_error('horainici','Si dia complet no fa falta hora inici')
            return cleaned_data
        if motiu=="A" and not observ:
            self.add_error('observacions', 'Si "Altres", s\'ha d\'explicar a observacions' )
        cleaned_data['datainici'] = datai
        cleaned_data['datafi'] = dataf
        cleaned_data['horainici'] = horai
        cleaned_data['horafi'] = horaf
        return cleaned_data
    