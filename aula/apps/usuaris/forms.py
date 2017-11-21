# This Python file uses the following encoding: utf-8
from aula.django_select2.forms import ModelSelect2Widget
from aula.utils.widgets import DateTextImput
from django.forms import ModelForm, ModelChoiceField
from django import forms
from django.contrib.auth.models import User
from aula.apps.usuaris.models import Professor
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
