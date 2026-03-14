# This Python file uses the following encoding: utf-8

from django import forms as forms
from django.forms import ModelForm
from django.forms.models import ModelChoiceField
from django_select2.forms import ModelSelect2Widget
from django.db.models import Q

from aula.apps.alumnes.models import (
    Alumne,
    AlumneGrup,
    AlumneNomSentitGrup,
    Curs,
    Grup,
    Nivell,
)
from aula.apps.usuaris.models import Professor
from aula.utils.widgets import bootStrapButtonSelect


class triaAlumneForm(forms.Form):
    nivell = forms.ModelChoiceField(
        queryset=Nivell.objects.all(),
        required=False,
        widget=ModelSelect2Widget(
            model=Nivell,
            search_fields=[
                "descripcio_nivell__icontains",
                "nom_nivell__icontains",
            ],
            attrs={"style": "width: 100%;", "data-minimum-input-length": 0},
        ),
    )

    curs = forms.ModelChoiceField(
        queryset=Curs.objects.all(),
        required=False,
        widget=ModelSelect2Widget(
            model=Curs,
            search_fields=[
                "nom_curs_complert__icontains",
                "nom_curs__icontains",
            ],
            dependent_fields={"nivell": "nivell"},
            attrs={"style": "width: 100%;", "data-minimum-input-length": 0},
        ),
    )

    grup = forms.ModelChoiceField(
        queryset=Grup.objects.all(),
        required=False,
        widget=ModelSelect2Widget(
            model=Grup,
            search_fields=[
                "descripcio_grup__icontains",
                "nom_grup__icontains",
            ],
            dependent_fields={"curs": "curs"},
            attrs={"style": "width: 100%;", "data-minimum-input-length": 0},
        ),
    )

    alumne = forms.ModelChoiceField(
        queryset=AlumneGrup.objects.all(),
        widget=ModelSelect2Widget(
            model=Alumne,
            search_fields=[
                "cognoms__icontains",
                "nom__icontains",
                "nom_sentit__icontains",
            ],
            dependent_fields={"grup": "grup"},
            attrs={"style": "width: 100%;", "data-minimum-input-length": 0},
        ),
    )


# ---form assignar grup -----------------------------------------------------------------------------------------
class grupForm(ModelForm):
    class Meta:
        model = Grup
        fields = ("curs", "nom_grup")


# ---form assignar tutor-----------------------------------------------------------------------------------------
class tutorsForm(forms.Form):
    grup = forms.CharField(widget=forms.TextInput(attrs={"readonly": True}))
    tutor1 = ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=Professor.objects.all(),
            search_fields=(
                "last_name__icontains",
                "first_name__icontains",
                "username__icontains",
            ),
            attrs={"style": "'width': '100%'"},
        ),
        queryset=Professor.objects.all(),
        required=False,
    )
    tutor2 = ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=Professor.objects.all(),
            search_fields=(
                "last_name__icontains",
                "first_name__icontains",
                "username__icontains",
            ),
            attrs={"style": "'width': '100%'"},
        ),
        queryset=Professor.objects.all(),
        required=False,
    )
    tutor3 = ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=Professor.objects.all(),
            search_fields=(
                "last_name__icontains",
                "first_name__icontains",
                "username__icontains",
            ),
            attrs={"style": "'width': '100%'"},
        ),
        queryset=Professor.objects.all(),
        required=False,
    )


# --tutoria individualitzada:
# from alumnes.models import Alumne
class triaMultiplesAlumnesForm(forms.Form):
    alumnes = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        help_text="""Pots triar o destriar més d'un alumne prement la tecla CTRL
                                                      mentre fas clic.
                                                      Per triar tots els alumnes selecciona el primer, 
                                                      baixa fins a l'últim i selecciona'l mantenint ara apretada
                                                      la tecla Shift ('Majúscules'),""",
    )

    def __init__(self, *args, **kwargs):
        self.queryset = kwargs.pop("queryset", None)
        self.etiqueta = kwargs.pop("etiqueta", None)
        super(triaMultiplesAlumnesForm, self).__init__(*args, **kwargs)
        self.fields["alumnes"].label = self.etiqueta
        self.fields["alumnes"].queryset = self.queryset


# ---------------- PROMOCIONS ------------------------#

__author__ = "David"
CHOICES = (
    ("0", "MOU"),
    ("1", "IGUAL"),
    ("2", "MARXA"),
)


class promoForm(ModelForm):
    decisio = forms.ChoiceField(
        widget=bootStrapButtonSelect(
            attrs={
                "class": "buttons-promos disabled",
            }
        ),
        choices=CHOICES,
    )

    class Meta:
        model = Alumne
        fields = []


class newAlumne(ModelForm):
    class Meta:
        model = Alumne
        # fields = ['grup', 'nom', 'cognoms', 'data_neixement', 'correu_tutors', 'correu_relacio_familia_pare', 'correu_relacio_familia_mare', 'tutors_volen_rebre_correu', 'centre_de_procedencia', 'localitat', 'telefons', 'tutors', 'adreca']
        fields = [
            "grup",
            "nom",
            "cognoms",
            "data_neixement",
            "rp1_nom",
            "rp1_telefon",
            "rp1_mobil",
            "rp1_correu",
            "rp2_nom",
            "rp2_telefon",
            "rp2_mobil",
            "rp2_correu",
            "correu_relacio_familia_pare",
            "correu_relacio_familia_mare",
            "tutors_volen_rebre_correu",
            "centre_de_procedencia",
            "localitat",
            "adreca",
        ]


# ----------------

############# Choice fields ###################


class triaAlumneSelect2Form(forms.Form):
    alumne = ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=AlumneGrup.objects.all(),
            search_fields=[
                "cognoms__icontains",
                "nom__icontains",
                "nom_sentit__icontains",
                "grup__descripcio_grup__icontains",
            ],
            attrs={"style": "'width': '100%'"},
        ),
        queryset=AlumneGrup.objects.all(),
        required=True,
    )


class triaAlumneNomSentitSelect2Form(forms.Form):
    alumne = ModelChoiceField(
        widget=ModelSelect2Widget(
            queryset=AlumneNomSentitGrup.objects.all(),
            search_fields=[
                "cognoms__icontains",
                "nom__icontains",
                "nom_sentit__icontains",
                "grup__descripcio_grup__icontains",
            ],
            attrs={"style": "'width': '100%'"},
        ),
        queryset=AlumneNomSentitGrup.objects.all(),
        required=True,
    )


# ---------------- CANVI DE GRUP PER BAIXES ------------------------


class ReassignarBaixesForm(forms.Form):

    grup_exist = forms.ModelChoiceField(
        # Selecciona els grups potencials per a moure les baixes: Sense tutor, sense horari i amb alumnes de baixa o sense alumnes.
        queryset=Grup.objects.exclude(tutor__isnull=False)
        .exclude(horari__isnull=False)
        .filter(Q(alumne__data_baixa__isnull=False) | Q(alumne__isnull=True))
        .distinct()
        .order_by("descripcio_grup"),
        required=False,
        label="Escollir grup existent",
    )

    crear_auto = forms.BooleanField(required=False, label="Crea grup automàtic BAIXES")

    nom_grup = forms.CharField(required=False, label="Grup nou per baixes")

    def clean(self):
        cleaned = super().clean()
        grup_exist = cleaned.get("grup_exist")
        crear_auto = cleaned.get("crear_auto")
        nom_grup = cleaned.get("nom_grup")
        # ---------- DESTÍ obligatori ----------
        if not (grup_exist or crear_auto or nom_grup):
            raise forms.ValidationError("Has d'indicar un destí")
        return cleaned
