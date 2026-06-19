"""
Vista per generar un PDF amb els markers AruCo dels alumnes tutorats.
"""

import io

import cv2
import matplotlib
import matplotlib.pyplot as plt
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.template.defaultfilters import slugify
from matplotlib import cm
from matplotlib.backends.backend_pdf import PdfPages

from aula.apps.usuaris.models import User2Professor
from aula.utils import tools
from aula.utils.decorators import group_required
from aula.utils.tools_aruco import is_aruco_actiu_per_grup

matplotlib.use("Agg")

# --- Constants de configuració ---
FIGSIZE = (8.27, 11.69)  # A4 vertical en polzades
INSET_LEFT = -0.005  # marge esquerre
INSET_BOTTOM = 0.10  # marge inferior
INSET_WIDTH = 1  # amplada del marcador
INSET_HEIGHT = 1  # alçada del marcador
TITLE_FONT_SIZE = 16
TITLE_PAD = 15


@login_required
@group_required(["professors"])
def imprimir(request):
    """
    Genera un PDF amb els markers AruCo dels alumnes tutorats
    (1 per pàgina A4 vertical, amb el màxim espai aprofitat)
    """

    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials
    professor = User2Professor(user)

    alumnes = [
        a
        for t in professor.tutor_set.all()
        for a in t.grup.alumne_set.all()
        if is_aruco_actiu_per_grup(t.grup)
    ]
    noms_i_markers = [
        (f"{a.grup} - {a.cognoms}, {a.nom}", int(a.aruco_marker)) for a in alumnes
    ]

    noms_i_markers.sort(key=lambda x: x[0])

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)

    buf = io.BytesIO()
    with PdfPages(buf) as pdf:
        for nom, marker_id in noms_i_markers:
            fig, ax = plt.subplots(figsize=FIGSIZE)

            ax.axis("off")

            marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, 2000)

            inset = ax.inset_axes([INSET_LEFT, INSET_BOTTOM, INSET_WIDTH, INSET_HEIGHT])
            inset.imshow(marker_img, cmap=cm.gray, interpolation="nearest")
            inset.axis("off")

            ax.set_title(nom, fontsize=TITLE_FONT_SIZE, pad=TITLE_PAD)

            pdf.savefig(fig)
            plt.close(fig)

    buf.seek(0)
    professor_slug = slugify(user.first_name + " " + user.last_name)
    return FileResponse(
        buf, as_attachment=True, filename=f"markers-tutor-{professor_slug}.pdf"
    )
