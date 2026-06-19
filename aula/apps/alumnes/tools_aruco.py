# This Python file uses the following encoding: utf-8
from typing import Dict, Optional, Set

from django.core.exceptions import ValidationError

from aula.apps.alumnes.models import Alumne, Curs, Grup, Nivell

FIRST_MARKER = 100
LAST_MARKER = 1024


def set_aruco_marker(
    alumne: Alumne,
    markers_cache: Optional[Dict[int, Set[int]]] = None,
):
    """
    Assigna un marker ARUCO a l'alumne.

    Procura que l'AruCo sigui únic en tots els nivells, però si no hi ha
    disponibles, assigna un marker únic per nivell, i, si no, per curs i
    si no, per grup.
    """
    if alumne.aruco_marker is not None:
        return  # Si ja té un marker assignat, no fem res.

    if markers_cache is None:
        markers_cache = dict_markers_disponibles()

    nivell_alumne = alumne.grup.curs.nivell.pk
    availables_by_nivell = markers_cache[nivell_alumne]

    availables_global = _global_markers_disponibles(markers_cache)

    if availables_global:
        # Assignem el primer marker disponible.
        alumne.aruco_marker = availables_global.pop()
        availables_by_nivell.discard(alumne.aruco_marker)
        return

    # Si no és de la ESO, busquem un marker global exceptuant ESO.
    # Per evitar que els que fan ICO o altres assignatures
    # compartides amb FP i BTX col·lisionin.
    if "ESO" not in alumne.grup.curs.nivell.nom_nivell.upper():
        availables_global_except_eso = _global_markers_disponibles_except_eso(
            markers_cache
        )
        if availables_global_except_eso:
            alumne.aruco_marker = availables_by_nivell.pop()
            availables_by_nivell.discard(alumne.aruco_marker)
            return

    availables_by_curs = _markers_disponibles_per_curs(alumne.grup.curs)
    if availables_by_curs:
        # Assignem el primer marker disponible del curs.
        alumne.aruco_marker = availables_by_curs.pop()
        availables_by_nivell.discard(alumne.aruco_marker)
        return

    availables_by_grup = _markers_disponibles_per_grup(alumne.grup)
    if availables_by_grup:
        # Assignem el primer marker disponible del grup.
        alumne.aruco_marker = availables_by_grup.pop()
        availables_by_nivell.discard(alumne.aruco_marker)
        return

    # Si no hi ha markers disponibles, validation error.
    raise ValidationError(
        f"No hi ha markers ARUCO disponibles per a l'alumne {alumne.nom} {alumne.cognoms}."
    )


def dict_markers_disponibles() -> Dict[int, Set[int]]:
    """
    Retorna un diccionari . La clau és el pk de nivell i
    els valors son els markers encara disponibles en aquell nivell.
    """
    nivells = Nivell.objects.all()
    markers = {nivell.pk: _markers_disponibles_per_nivell(nivell) for nivell in nivells}
    return markers


#
#
# Helpers per a la gestió de markers disponibles
#


def _global_markers_disponibles(dit_makers: Dict[int, Set[int]]) -> Set[int]:
    """
    Intersect of all markers disponibles per nivell.
    """

    return set.intersection(*dit_makers.values())


def _global_markers_disponibles_except_eso(
    dit_makers: Dict[int, Set[int]],
) -> Set[int]:
    """
    Intersect of all markers disponibles per nivell exceptuant ESO.
    """
    eso_pk = Nivell.objects.filter(nom_nivell__icontains="ESO").values_list("pk", flat=True)
    dit_makers_no_eso = {
        pk: markers for pk, markers in dit_makers.items() if pk not in eso_pk
    }
    return set.intersection(*dit_makers_no_eso.values()) if dit_makers_no_eso else set()


def _markers_disponibles_per_nivell(nivell: Nivell):
    """
    Retorna un conjunt amb els markers disponibles per assignar a alumnes.
    Els markers són números enters de 0 a 1022.
    Els 100 primers estan reservats per a l'assignació manual.
    """
    all_markers = _get_all_markers()
    markers_pillats = set(
        Alumne.objects.filter(grup__curs__nivell=nivell).values_list(
            "aruco_marker", flat=True
        )
    )
    return all_markers - markers_pillats


def _markers_disponibles_per_curs(curs: Curs):
    """
    Retorna un conjunt amb els markers disponibles per assignar a alumnes.
    Els markers són números enters de 0 a 1022.
    Els 100 primers estan reservats per a l'assignació manual.
    """
    all_markers = _get_all_markers()
    markers_pillats = set(
        Alumne.objects.filter(grup__curs=curs).values_list("aruco_marker", flat=True)
    )
    return all_markers - markers_pillats


def _markers_disponibles_per_grup(grup: Grup):
    """
    Retorna un conjunt amb els markers disponibles per assignar a alumnes.
    Els markers són números enters de 0 a 1022.
    Els 100 primers estan reservats per a l'assignació manual.
    """
    all_markers = _get_all_markers()
    markers_pillats = set(
        Alumne.objects.filter(grup=grup).values_list("aruco_marker", flat=True)
    )
    return all_markers - markers_pillats


def _get_all_markers() -> Set[int]:
    """
    Retorna un conjunt amb tots els markers disponibles.
    Els markers són números enters de 0 a 1022.
    Els 100 primers estan reservats per a l'assignació manual.
    """
    return set(range(FIRST_MARKER, LAST_MARKER))
