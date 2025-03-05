"""Filtre per a la llista de sortides o pagaments."""

from django.apps import apps
from django.db.models import Q
import django_filters

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit

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
    tipus = django_filters.ChoiceFilter(
        choices=Sortida.TIPUS_ACTIVITAT_CHOICES, label="Tipus"
    )
    mitja_de_transport = django_filters.CharFilter(
        lookup_expr="icontains", label="Mitjà de transport"
    )
    empresa_de_transport = django_filters.CharFilter(
        lookup_expr="icontains", label="Empresa de transport"
    )

    data_inici_desde = django_filters.DateFilter(
        field_name="data_inici",
        lookup_expr="gte",
        label="Data d'inici (des de)",
        widget=DateTextImput(),
    )

    data_inici_fins = django_filters.DateFilter(
        field_name="data_inici",
        lookup_expr="lte",
        label="Data d'inici (fins a)",
        widget=DateTextImput(),
    )

    # init
    def __init__(self, *args, tipus=None, **kwargs):
        """Init: set queryset and other settings"""
        super(SortidaFilter, self).__init__(*args, **kwargs)

        Professor = apps.get_model("usuaris", "Professor")
        self.filters["professor"].queryset = (
            Professor.objects.all()
        )  # Set queryset dynamically

        extra_divs = [
            Div(Field("ambit", css_class="form-control"), css_class="col-lg-4"),
            Div(Field("tipus", css_class="form-control"), css_class="col-lg-4"),
        ]
        if tipus == "P":
            # remove 'tipus' from filter fields
            self.filters.pop("tipus")
            self.filters.pop("ciutat")

        # Crispy Forms Helper
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.form_class = "form-inline"
        self.helper.layout = self.helper.layout = Layout(
            Div(
                *extra_divs,
                Div(Field("subtipus", css_class="form-control"), css_class="col-lg-4"),
                Div(Field("estat", css_class="form-control"), css_class="col-lg-4"),
                Div(Field("titol", css_class="form-control"), css_class="col-lg-4"),
                Div(Field("ciutat", css_class="form-control"), css_class="col-lg-4"),
                Div(
                    Field("mitja_de_transport", css_class="form-control"),
                    css_class="col-lg-4",
                ),
                Div(
                    Field("empresa_de_transport", css_class="form-control"),
                    css_class="col-lg-4",
                ),
                css_class="row",
            ),
            Div(
                Div(
                    Field("data_inici_desde", css_class="form-control"),
                    css_class="col-lg-4",
                ),
                Div(
                    Field("data_inici_fins", css_class="form-control"),
                    css_class="col-lg-4",
                ),
                css_class="row",
            ),
            Submit("submit", "Filtrar", css_class="btn btn-primary"),
        )

    class Meta:  # pylint: disable=too-few-public-methods
        """Configuració del filtre."""

        model = Sortida
        fields = [
            "estat",
            "tipus",
            "subtipus",
            "titol",
            "ambit",
            "ciutat",
            "mitja_de_transport",
            "empresa_de_transport",
            "data_inici_desde",
            "data_inici_fins",
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
