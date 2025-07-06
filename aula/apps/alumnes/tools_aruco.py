# This Python file uses the following encoding: utf-8
from typing import Optional, Set

from django.core.exceptions import ValidationError

from aula.apps.alumnes.models import Alumne, Curs, Grup, Nivell


def set_aruco_marker(alumne: Alumne, available_markers: Optional[Set[int]] = None):
    if alumne.aruco_marker is not None:
        return  # Si ja té un marker assignat, no fem res.
    if available_markers is None:
        available_markers = markers_disponibles_per_nivell(alumne.grup.curs.nivell)

    if available_markers:
        # Assignem el primer marker disponible.
        alumne.aruco_marker = available_markers.pop()
        return

    availables_by_curs = markers_disponibles_per_curs(alumne.grup.curs)
    if availables_by_curs:
        # Assignem el primer marker disponible del curs.
        alumne.aruco_marker = availables_by_curs.pop()
        return

    availables_by_grup = markers_disponibles_per_grup(alumne.grup)
    if availables_by_grup:
        # Assignem el primer marker disponible del grup.
        alumne.aruco_marker = availables_by_grup.pop()
        return

    # Si no hi ha markers disponibles, validation error.
    raise ValidationError(
        f"No hi ha markers ARUCO disponibles per a l'alumne {alumne.nom} {alumne.cognoms}."
    )


def markers_disponibles() -> dict[int, Set[int]]:
    """
    Retorna un diccionari de pk de nivells i els markers disponibles per assignar a alumnes.
    """
    nivells = Nivell.objects.all()
    markers = {nivell.pk: markers_disponibles_per_nivell(nivell) for nivell in nivells}
    return markers


def markers_disponibles_per_nivell(nivell: Nivell):
    """
    Retorna un conjunt amb els markers disponibles per assignar a alumnes.
    Els markers són números enters de 0 a 1022.
    Els 100 primers estan reservats per a l'assignació manual.
    """
    all_markers = set(range(100, 1023))
    markers_pillats = set(
        Alumne.objects.filter(grup__curs__nivell=nivell).values_list(
            "aruco_marker", flat=True
        )
    )
    return all_markers - markers_pillats


def markers_disponibles_per_curs(curs: Curs):
    """
    Retorna un conjunt amb els markers disponibles per assignar a alumnes.
    Els markers són números enters de 0 a 1022.
    Els 100 primers estan reservats per a l'assignació manual.
    """
    all_markers = set(range(100, 1023))
    markers_pillats = set(
        Alumne.objects.filter(grup__curs=curs).values_list("aruco_marker", flat=True)
    )
    return all_markers - markers_pillats


def markers_disponibles_per_grup(grup: Grup):
    """
    Retorna un conjunt amb els markers disponibles per assignar a alumnes.
    Els markers són números enters de 0 a 1022.
    Els 100 primers estan reservats per a l'assignació manual.
    """
    all_markers = set(range(100, 1023))
    markers_pillats = set(
        Alumne.objects.filter(grup=grup).values_list("aruco_marker", flat=True)
    )
    return all_markers - markers_pillats
