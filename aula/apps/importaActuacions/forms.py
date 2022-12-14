from django import forms

class dades_dboldForm (forms.Form):
    nom = forms.CharField(label='Nom de la Base de dades antiga:', max_length=30)
    usuari = forms.CharField(label='Usuari per accedir-hi:', max_length=30)
    contrasenya = forms.CharField(label="Contrasenya de l'usuari:", max_length=30, widget=forms.PasswordInput)
