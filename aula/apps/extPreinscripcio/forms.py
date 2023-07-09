from django import forms as forms
from aula.apps.extPreinscripcio.sincronitza import testMatActiva

class PreinscripcioForm(forms.Form):
    fitxer_Preinscripcio = forms.FileField(required=True, label="Fitxer de la preinscripció")
    resetPrevious=forms.BooleanField(label=u"Elimina dades anteriors",required = False,
                                help_text=u"S'esborren preinscripcions pendents, d'activació de matrícula, dels mateixos \
                                estudis. No s'ha de fer servir si volem carregar preinscripcions des de diversos fitxers.")

    def clean(self):
        cleaned_data = super().clean()
        f=cleaned_data.get('fitxer_Preinscripcio')
        matActiva, missatge = testMatActiva(f)
        if matActiva or missatge:
            # Hi ha alguna preinscripció amb matrícula activa per als mateixos estudis
            # o s'ha produit un error d'accés al fitxer.
            self.add_error('fitxer_Preinscripcio', missatge)
        return cleaned_data