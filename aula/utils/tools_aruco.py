from django.conf import settings

from aula.apps.alumnes.models import Grup


def is_aruco_actiu_per_grup(grup: Grup) -> bool:
    """
    Comprova si els marcadors Aruco estan actius per a aquest impartir.
    # Estarà actiu:
    # si '*' és a la llista o
    # si impartir.horari.grup.descripcio_grup és a la llista o
    # si impartir.horari.grup.curs.nom_curs_complert és a la llista o
    # si impartir.horari.grup.curs.nivell.descripcio_nivell és a la llista
    """
    llista = settings.ARUCO_ACTIU or []
    if "*" in llista:
        return True
    if not grup:
        return False
    if grup.descripcio_grup in llista:
        return True
    if grup.curs.nom_curs_complert in llista:
        return True
    if grup.curs.nivell.descripcio_nivell in llista:
        return True
    return False
