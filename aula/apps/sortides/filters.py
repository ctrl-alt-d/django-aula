import django_filters
from aula.apps.sortides.models import Sortida
from django.apps import apps
from django.db.models import Q


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

    # init
    def __init__(self, *args, tipus=None, **kwargs):
        super(SortidaFilter, self).__init__(*args, **kwargs)

        Professor = apps.get_model("usuaris", "Professor")
        self.filters["professor"].queryset = (
            Professor.objects.all()
        )  # Set queryset dynamically

        if tipus == "P":
            # remove 'tipus' from filter fields
            self.filters.pop("tipus")
            self.filters.pop("ciutat")

    class Meta:
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
