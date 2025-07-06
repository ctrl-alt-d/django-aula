import io
from django.http import FileResponse

import matplotlib

matplotlib.use("Agg")  # Safe backend for Django

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import cm
import cv2

from aula.apps.usuaris.models import User2Professor
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required
from aula.utils import tools


@login_required
@group_required(["professors",])
def imprimir(request):
    """
    Genera un PDF amb els markers AruCo dels alumnes tutorats (2 per pàgina A4 horitzontal)
    """

    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials
    professor = User2Professor(user)

    alumnes = [a for t in professor.tutor_set.all() for a in t.grup.alumne_set.all()]

    noms_i_markers = [(f"{a.nom} {a.cognoms}", int(a.aruco_marker)) for a in alumnes]

    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

    buf = io.BytesIO()
    with PdfPages(buf) as pdf:
        for i in range(0, len(noms_i_markers), 2):
            fig, axs = plt.subplots(1, 2, figsize=(11.69, 8.27))  # A4 landscape

            for j in range(2):
                ax = axs[j]
                if i + j < len(noms_i_markers):
                    nom, marker_id = noms_i_markers[i + j]
                    marker_img = cv2.aruco.generateImageMarker(
                        aruco_dict, marker_id, 400
                    )
                    ax.imshow(marker_img, cmap=cm.gray, interpolation="nearest")
                    ax.set_title(nom, fontsize=16)
                    ax.axis("off")
                else:
                    ax.axis("off")  # Hide empty subplot

            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

    buf.seek(0)

    professor_slug = slugify(user.first_name + " " + user.last_name)
    return FileResponse(
        buf, as_attachment=True, filename=f"markers-tutor-{professor_slug}.pdf"
    )
