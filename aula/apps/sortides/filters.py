"""Filtre per a la llista de sortides o pagaments."""

from django.apps import apps
from django.db.models import Q
import django_filters
from django.db.models.functions import TruncDate

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit, Fieldset, HTML

from aula.apps.sortides.models import Sortida
from aula.utils.widgets import DateTextImput


class SortidaFilter(django_filters.FilterSet):
    """
    Filtre per a la llista de sortides o pagaments.
    """

    professor = django_filters.ModelChoiceFilter(
        queryset=None,  # Temporarily set to None
        method="filter_by_professor",
        label="Professor responsable o acompanyant",
    )
    titol = django_filters.CharFilter(lookup_expr="icontains", label="Títol")
    ambit = django_filters.CharFilter(lookup_expr="icontains", label="Àmbit")
    ciutat = django_filters.CharFilter(lookup_expr="icontains", label="Ciutat")
    mitja_de_transport = django_filters.CharFilter(
        lookup_expr="icontains", label="Mitjà de transport"
    )
    empresa_de_transport = django_filters.CharFilter(
        lookup_expr="icontains", label="Empresa de transport"
    )

    data_inici_desde = django_filters.DateFilter(
        method="filter_calendari_desde",
        label="Rang data inici des de",
        help_text="Inici igual o posterior a data",
        widget=DateTextImput(),
    )

    data_inici_fins = django_filters.DateFilter(
        method="filter_calendari_fins",
        label="Rang data inici fins a",
        help_text="Inici igual o anterior a data",
        widget=DateTextImput(),
    )

    termini_pagament_desde = django_filters.DateFilter(
        field_name="termini_pagament",
        lookup_expr="date__gte",
        label="Rang termini pagament des de",
        help_text="Termini pagament igual o posterior a data",
        widget=DateTextImput(),
    )

    termini_pagament_fins = django_filters.DateFilter(
        field_name="termini_pagament",
        lookup_expr="date__lte",
        label="Rang termini pagament fins a",
        help_text="Termini pagament igual o anterior a data",
        widget=DateTextImput(),
    )

    # init
    def __init__(self, *args, **kwargs):
        """Init: set queryset and other settings"""
        super(SortidaFilter, self).__init__(*args, **kwargs)

        Professor = apps.get_model("usuaris", "Professor")
        self.filters["professor"].queryset = (
            Professor.objects.all()
        )  # Set queryset dynamically

        # Crispy Forms Helper
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.form_class = "form-inline"

        self.helper.layout = Layout(
            Fieldset(
                "Criteris de cerca",
                Div(
                    Field("estat", css_class="form-control form-control-sm"),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field("subtipus", css_class="form-control form-control-sm"),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field("titol", css_class="form-control form-control-sm"),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field("ciutat", css_class="form-control form-control-sm"),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field("ambit", css_class="form-control form-control-sm"),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field(
                        "mitja_de_transport", css_class="form-control form-control-sm"
                    ),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field(
                        "empresa_de_transport", css_class="form-control form-control-sm"
                    ),
                    css_class="col-lg-4 small",
                ),
                css_class="row small",
            ),
            Fieldset(
                "Rang data d'inici",
                Div(
                    Field("data_inici_desde", css_class="form-control form-control-sm"),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field("data_inici_fins", css_class="form-control form-control-sm"),
                    css_class="col-lg-4 small",
                ),
                css_class="row small",
            ),
            Fieldset(
                "Rang dates de pagament",
                Div(
                    Field(
                        "termini_pagament_desde",
                        css_class="form-control form-control-sm",
                    ),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field(
                        "termini_pagament_fins",
                        css_class="form-control form-control-sm",
                    ),
                    css_class="col-lg-4 small",
                ),
                css_class="row small",
            ),
            Submit("submit", "Filtrar", css_class="btn btn-primary btn-sm"),
        )

    class Meta:  # pylint: disable=too-few-public-methods
        """Configuració del filtre."""

        model = Sortida
        fields = [
            "estat",
            "subtipus",
            "titol",
            "ambit",
            "ciutat",
            "mitja_de_transport",
            "empresa_de_transport",
            "termini_pagament_desde",
            "termini_pagament_fins",
        ]

    @property
    def form(self):
        """
        Sobreescric el form per tal d'afegir la classe 'form-control' als widgets
        """
        form = super().form
        for field in form.fields.values():
            field.widget.attrs.update({"class": "form-control"})
        return form

    def filter_by_professor(self, queryset, name, value):
        """
        Filters Sortida by a Professor instance,
        checking both `professor_que_proposa`
        and `professors_responsables` fields.
        """
        return queryset.filter(
            Q(professor_que_proposa=value) | Q(professors_responsables=value)
        ).distinct()

    def filter_calendari_desde(self, queryset, name, value):
        return queryset.filter(calendari_desde__date__gte=value)

    def filter_calendari_fins(self, queryset, name, value):
        return queryset.filter(calendari_desde__date__lte=value)

class PagamentFilter(django_filters.FilterSet):
    """
    Filtre per a la llista de sortides o pagaments.
    """

    professor = django_filters.ModelChoiceFilter(
        queryset=None,  # Temporarily set to None
        method="filter_by_professor",
        label="Professor que proposa",
    )
    departament_que_organitza = django_filters.ModelChoiceFilter(
        queryset=None,  # Temporarily set to None
    )
    tipus = django_filters.ChoiceFilter(
        choices=Sortida.TIPUS_ACTIVITAT_CHOICES, label="Tipus"
    )

    titol = django_filters.CharFilter(lookup_expr="icontains", label="Títol")
    ambit = django_filters.CharFilter(lookup_expr="icontains", label="Àmbit")
    
    subtipus = django_filters.ChoiceFilter(
        choices=[(f"P{k}", v) for k, v in Sortida.SUBTIPUS_ACTIVITAT['P']],
        label="Tipus"
    )
        

    termini_pagament_desde = django_filters.DateFilter(
        field_name="termini_pagament",
        lookup_expr="date__gte",
        label="Termini pagament posterior a",
        widget=DateTextImput(),
    )

    termini_pagament_fins = django_filters.DateFilter(
        field_name="termini_pagament",
        lookup_expr="date__lte",
        label="Termini pagament anterior a",
        widget=DateTextImput(),
    )

    # init
    def __init__(self, *args, **kwargs):
        """Init: set queryset and other settings"""
        super(PagamentFilter, self).__init__(*args, **kwargs)

        Professor = apps.get_model("usuaris", "Professor")
        self.filters["professor"].queryset = (
            Professor.objects.all()
        )  # Set queryset dynamically

        Departament = apps.get_model("usuaris", "Departament")
        self.filters["departament_que_organitza"].queryset = Departament.objects.all()

        # Crispy Forms Helper
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.form_class = "form-inline"
        self.helper.layout = Layout(
            Fieldset(
                "Criteris de cerca",
                Div(
                    Field("estat", css_class="form-control form-control-sm"),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field(
                        "subtipus", css_class="form-control form-control-sm"
                    ),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field("titol", css_class="form-control form-control-sm"),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field("ambit", css_class="form-control form-control-sm"),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field(
                        "departament_que_organitza",
                        css_class="form-control form-control-sm",
                    ),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field(
                        "tipus_de_pagament", css_class="form-control form-control-sm"
                    ),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field("professor", css_class="form-control form-control-sm"),
                    css_class="col-lg-4 small",
                ),
                css_class="row small fieldset-small",
            ),
            Fieldset(
                "Rang dates de pagament",
                Div(
                    Field(
                        "termini_pagament_desde",
                        css_class="form-control form-control-sm",
                    ),
                    css_class="col-lg-4 small",
                ),
                Div(
                    Field(
                        "termini_pagament_fins",
                        css_class="form-control form-control-sm",
                    ),
                    css_class="col-lg-4 small",
                ),
                css_class="row small fieldset-small",
            ),
            Submit("submit", "Filtrar", css_class="btn btn-primary btn-sm"),
        )

    class Meta:  # pylint: disable=too-few-public-methods
        """Configuració del filtre."""

        model = Sortida
        fields = [
            "estat",
            "subtipus",
            "titol",
            "ambit",
            "departament_que_organitza",
            "tipus_de_pagament",
            "professor",
            "termini_pagament_desde",
            "termini_pagament_fins",
        ]

    @property
    def form(self):
        """
        Sobreescric el form per tal d'afegir la classe 'form-control' als widgets
        """
        form = super().form
        for field in form.fields.values():
            field.widget.attrs.update({"class": "form-control"})
        return form

    def filter_by_professor(self, queryset, name, value):
        """
        Filters Sortida by a Professor instance,
        checking both `professor_que_proposa`
        and `professors_responsables` fields.
        """
        return queryset.filter(
            Q(professor_que_proposa=value) | Q(professors_responsables=value)
        ).distinct()
