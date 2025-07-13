"""
Helpers per passar llista amb Aruco.
"""

from aula.apps.presencia.models import Impartir
from aula.utils.tools_aruco import is_aruco_actiu_per_grup


def get_aruco_impartir_ctx(impartir: Impartir) -> dict:
    """
    Prepara el context per a la visualització de l'Impartir amb Aruco.
    """

    grup = impartir.horari.grup
    actiu_per_aquest_impartir = is_aruco_actiu_per_grup(grup)

    if not actiu_per_aquest_impartir:
        # No està actiu, retornem un context buit
        resultat = _get_empty_context()
        return resultat

    # Si està actiu, preparem el context
    resultat = _fill_context(impartir)
    return resultat


# ------
# Funcions privades per a la preparació del context
# ------


def _fill_context(impartir):
    """
    Prepara el context per a la visualització de l'Impartir amb Aruco.
    """
    controls_assistencia = impartir.controlassistencia_set.all()

    def esta_justificat(control_a):
        """
        Comprova si està marcat com a justificat.
        """
        return control_a.estat is not None and control_a.estat.codi_estat == "J"

    def alumne_fora_de_laula(control_a):
        """
        Comprova si l'alumne no ha de ser a l'aula.
        """
        return control_a.nohadeseralaula_set.exists()

    def puc_passar_llista_alumne(control_a):
        """
        Comprova si es pot passar llista a l'alumne.
        """
        return not esta_justificat(control_a) and not alumne_fora_de_laula(control_a)

    controls_aula = [
        control_a
        for control_a in controls_assistencia
        if puc_passar_llista_alumne(control_a)
    ]

    aruco_marker2control = {
        control_a.alumne.aruco_marker: f"rad_id_{control_a.pk}-estat_"
        for control_a in controls_aula
    }

    aruco_marker2alumne = {
        control_a.alumne.aruco_marker: f"{control_a.alumne.nom} {control_a.alumne.cognoms}"
        for control_a in controls_aula
    }

    hi_ha_arucos_repetits = len(controls_aula) != len(aruco_marker2alumne)

    aruco_disponible = not hi_ha_arucos_repetits and len(aruco_marker2alumne) > 0

    aruco_no_disponible_txt = (
        "Hi ha alumnes amb Aruco repetit"
        if hi_ha_arucos_repetits
        else "No hi ha alumnes a aquesta hora" if len(controls_aula) == 0 else ""
    )

    resultat = {
        "aruco_marker2alumne": aruco_marker2alumne,
        "aruco_marker2control": aruco_marker2control,
        "aruco_disponible": aruco_disponible,
        "aruco_no_disponible_txt": aruco_no_disponible_txt,
    }

    return resultat


def _get_empty_context():
    """
    Retorna un context buit per a quan els marcadors Aruco no estan actius.
    """
    resultat = {
        "aruco_marker2alumne": {},
        "aruco_marker2control": {},
        "aruco_disponible": False,
        "aruco_no_disponible_txt": "",
    }

    return resultat
