from django.urls import path

from aula.apps.extPreinscripcio.views import assignaNivells, importaFitxer

urlpatterns = [
    path("importa/", importaFitxer, name="administracio__sincronitza__preinscripcio"),
    path(
        "assignaNivells/",
        assignaNivells,
        name="administracio__configuracio__preinscripcio",
    ),
]
