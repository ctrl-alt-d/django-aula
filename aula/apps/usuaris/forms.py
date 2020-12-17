# This Python file uses the following encoding: utf-8
from django.forms.models import ModelMultipleChoiceField

from aula.django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget
from aula.utils.widgets import DateTextImput
from django.forms import ModelForm, ModelChoiceField
from django import forms
from django.contrib.auth.models import User
from aula.apps.usuaris.models import Professor, ProfessorConserge, DadesAddicionalsProfessor
import imghdr
from aula.settings import CUSTOM_TIPUS_MIME_FOTOS
from PIL import Image
import io, os
from django.core.files.uploadedfile import InMemoryUploadedFile

#from aula.utils.captcha import ReCaptchaField

class CanviDadesUsuari(ModelForm):
    first_name = forms.CharField( required = True )  
    last_name = forms.CharField( required = True )  
    email = forms.EmailField( required = True )  
    class Meta:
        model = User
        fields = ('first_name', 'last_name','email')
        
    def clean(self):
        totInformat = self.cleaned_data.get('first_name') and self.cleaned_data.get('last_name') and self.cleaned_data.get('email')
        if not totInformat:
            raise forms.ValidationError('Cal informar totes les dades')
        return self.cleaned_data

class CanviDadesAddicionalsUsuari(ModelForm):
    foto = forms.ImageField(required=False)

    class Meta:
        model = DadesAddicionalsProfessor
        fields = ('foto',)

    def clean_foto(self):
        foto = self.cleaned_data['foto']
        if foto and 'image/{0}'.format(imghdr.what(foto)) not in CUSTOM_TIPUS_MIME_FOTOS:
            message = "Tipus de fitxer no vàlid. Formats permesos: {0}".format(CUSTOM_TIPUS_MIME_FOTOS).replace("image/",'')
            raise forms.ValidationError(message)
        return foto

    def save(self):
        # redimensionar i utilitzar username com a nom de foto
        try:
            img = Image.open(self.files['foto'])
            img.thumbnail((150, 150), Image.ANTIALIAS)
            thumb_io = io.BytesIO()
            img.save(thumb_io, self.files['foto'].content_type.split('/')[-1].upper())
            new_file_name = 'profe_' + str(self.instance.professor.username) + os.path.splitext(self.instance.foto.name)[1]
            file = InMemoryUploadedFile(thumb_io,
                                        u"foto",
                                        new_file_name,
                                        self.files['foto'].content_type,
                                        thumb_io.getbuffer().nbytes,
                                        None)
            self.instance.foto = file
        except:
            pass
        super(CanviDadesAddicionalsUsuari, self).save()

class triaUsuariForm(forms.Form):
    professor = forms.ModelChoiceField( 
                        queryset= Professor.objects.all(),
                        required= True,
                        help_text=u'Tria en quin usuari et vols convertir.',
                        widget=ModelSelect2Widget(
                            queryset=Professor.objects.all(),
                            search_fields=['last_name__icontains', 'first_name__icontains'],
                            attrs={'style': "'width': '100%'"}
                        ),
                    )


class loginUsuariForm(forms.Form):
    usuari = forms.CharField(  required = True,
                               help_text= u"Nom d'usuari" )
    paraulaDePas = forms.CharField(label="Paraula de Pas" , required = True,
                               help_text= u"Paraula de pas", widget = forms.PasswordInput() )
    
    
class recuperacioDePasswdForm(forms.Form):
    p1 = forms.CharField(label="Nova Paraula de Pas" , required = True,
                               help_text= u"Paraula de pas, més de 6 caracters.", widget = forms.PasswordInput() )
    p2 = forms.CharField(label="Repeteix Paraula de Pas" , required = True,
                               help_text= u"Paraula de pas, més de 6 caracters.", widget = forms.PasswordInput() )
    data_neixement = forms.DateField(label="Data naixement", help_text=u"Data de naixement de l'alumne (Format dd/mm/yyyy)", widget=  DateTextImput( ) )
    
    def clean_p1(self):
        p1 = self.cleaned_data.get('p1')
        if len( p1 ) < 6:
            raise forms.ValidationError("La Paraula de Pas ha de tenir 6 ó més caracters.")
        return p1       
    
    def clean_p2(self):
        p1 = self.cleaned_data.get('p1')
        p2 = self.cleaned_data.get('p2')
        if not p2:
            raise forms.ValidationError("Cal confirmar la Contrasenya")
        if p1 != p2:
            raise forms.ValidationError("Has escrit dues contrasenyes diferents")
        return p2

class canviDePasswdForm(forms.Form):
    p0 = forms.CharField(label="Paraula de pas actual" , required = True,
                               help_text= u"Paraula de pas actual, la que tens actualment.", widget = forms.PasswordInput() )
    p1 = forms.CharField(label="Nova Paraula de Pas" , required = True,
                               help_text= u"Paraula de pas, més de 6 caracters.", widget = forms.PasswordInput() )
    p2 = forms.CharField(label="Repeteix Paraula de Pas" , required = True,
                               help_text= u"Paraula de pas, més de 6 caracters.", widget = forms.PasswordInput() )

    def clean_p1(self):
        p1 = self.cleaned_data.get('p1')
        if len( p1 ) < 6:
            raise forms.ValidationError("La Paraula de Pas ha de tenir 6 ó més caracters.")
        return p1       
    
    def clean_p2(self):
        p1 = self.cleaned_data.get('p1')
        p2 = self.cleaned_data.get('p2')
        if not p2:
            raise forms.ValidationError("Cal confirmar la Contrasenya")
        if p1 != p2:
            raise forms.ValidationError("Has escrit dues contrasenyes diferents")
        return p2

class sendPasswdByEmailForm(forms.Form):
    email = forms.EmailField(label=u"El teu correu electrònic" , required = True,
                               help_text= u"Entra el teu correu electrònic." )   
    #captcha = ReCaptchaField()


class triaProfessorSelect2Form(forms.Form):
    professor = ModelChoiceField(
                   widget=ModelSelect2Widget(
                                        queryset=Professor.objects.all(),
                                        search_fields =('last_name__icontains', 'first_name__icontains',),
                                        attrs={'style':"'width': '100%'"}
                                                    ),
                   queryset=Professor.objects.all(),
                   required=True)


class triaProfessorsConsergesSelect2Form(forms.Form):
    professors_conserges = ModelMultipleChoiceField(
                   label="Tria professors o PAS",
                   widget=ModelSelect2MultipleWidget(
                                        queryset=ProfessorConserge.objects.all(),
                                        search_fields =('last_name__icontains', 'first_name__icontains',),
                                        attrs={'style':"'width': '100%'"}
                                                    ),
                   queryset=ProfessorConserge.objects.all(),
                   required=True)
