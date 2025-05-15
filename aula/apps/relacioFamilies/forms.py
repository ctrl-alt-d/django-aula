import imghdr
import io
import os

from PIL import Image
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile

from aula.apps.alumnes.models import Alumne
from aula.apps.relacioFamilies.models import Responsable
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
        fields = ['responsable_preferent', 'correu', 'periodicitat_faltes', 'periodicitat_incidencies', 'foto', 'observacions']
        labels = {
            'correu': "Correu de l'alumne",
            }
    
    def __init__(self, tutor, *args, **kwargs):
        super(AlumneModelForm, self).__init__(*args, **kwargs)
        if tutor:
            responsables = self.instance.get_responsables()
            if not any(responsables):
                self.fields.pop('responsable_preferent')
            else:
                responsable_choices = [(x.id, x.get_nom()) for x in responsables if x]
                self.fields['responsable_preferent'] = forms.ChoiceField(choices=responsable_choices)
                self.fields['responsable_preferent'].help_text = "Responsable preferent de l'alumne/a"
                self.fields['responsable_preferent'].label = "Responsable preferent"
        else:
            self.fields.pop('responsable_preferent')

    def clean_foto(self):
        foto = self.cleaned_data['foto']
        ok, mess = tipusFotoOK(foto)
        if not ok:
            raise forms.ValidationError(mess)
        return foto
    
    def clean_responsable_preferent(self):
        respid=self.cleaned_data['responsable_preferent']
        try:
            resp=Responsable.objects.get(id=respid)
        except:
            resp=None
        return resp

    def save(self):
        #redimensionar i utilitzar ralc com a nom de foto
        try:
            self.instance.foto = convertirFoto(self.files['foto'], self.instance.ralc, self.instance.foto)
        except: pass
        super(AlumneModelForm, self).save()

class ResponsableModelForm(forms.ModelForm):
    custom_names = {'correu_relacio_familia': None,
                    'periodicitat_faltes': None,
                    'periodicitat_incidencies': None,
                    }
    
    class Meta:
        model = Responsable
        fields = ['correu_relacio_familia', 'periodicitat_faltes', 'periodicitat_incidencies']
        
    def __init__(self, prefix, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_names={
            'correu_relacio_familia': prefix+'_correu_relacio_familia',
            'periodicitat_faltes': prefix+'_periodicitat_faltes',
            'periodicitat_incidencies': prefix+'_periodicitat_incidencies',
            }
        self.fields['correu_relacio_familia'].label='Correu responsable '+ self.instance.get_nom()
        # DEPRECATED vvv
        if not self.instance.dni:
            self.fields['correu_relacio_familia'].widget.attrs['readonly'] = True
            self.fields['periodicitat_faltes'].widget.attrs['readonly'] = True
            self.fields['periodicitat_faltes'].disabled = True
            self.fields['periodicitat_incidencies'].widget.attrs['readonly'] = True
            self.fields['periodicitat_incidencies'].disabled = True
        # DEPRECATED ^^^
    
    def add_prefix(self, field_name):
        field_name = self.custom_names.get(field_name, field_name)
        return super().add_prefix(field_name)
    
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

    def clean_observacions(self):
        from itertools import groupby
        import re
        
        motiu=self.cleaned_data['motiu']
        observ=self.cleaned_data['observacions']
        if motiu=="A" and not bool(observ):
            raise forms.ValidationError('Si "Altres", s\'ha d\'explicar a observacions')
        ncar=0
        if bool(observ): ncar=len(list(groupby(sorted(re.sub(r'[^a-zA-Z]', '', observ)))))
        if bool(observ) and ncar<5:
            raise forms.ValidationError('Si us plau, afegeixi una mica més de detall a observacions')
        return observ

    def clean(self):
        from aula.apps.horaris.models import FranjaHoraria
        cleaned_data = super().clean()
        datai=cleaned_data.get('datainici')
        dataf=cleaned_data.get('datafi')
        horai=cleaned_data.get('horainici')
        horaf=cleaned_data.get('horafi')
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
        cleaned_data['datainici'] = datai
        cleaned_data['datafi'] = dataf
        cleaned_data['horainici'] = horai
        cleaned_data['horafi'] = horaf
        return cleaned_data

class escollirAlumneForm(forms.Form):
    
    alumne=forms.ChoiceField(label=u"Selecciona l'alumne a gestionar",
                                required=True,
                                widget=forms.RadioSelect())
    
    def __init__(self, user, responsable, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['alumne'].choices=[ (a.id, a.nom+" "+a.cognoms) for a in responsable.get_alumnes_associats()]
