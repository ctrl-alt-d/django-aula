# This Python file uses the following encoding: utf-8

import calendar
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

#  amorilla@xtec.cat
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.templatetags.static import static
from django.utils import timezone
from private_storage.fields import PrivateFileField

from aula.apps.alumnes.named_instances import Cursa_nivell, Nivells_no_obligatoris
from aula.apps.tutoria.models import SeguimentTutorial
from aula.apps.usuaris.models import AlumneUser, Professor
from aula.settings import CUSTOM_TIPUS_MIME_FOTOS


class AbstractNivell(models.Model):
    nom_nivell = models.CharField("Nom nivell", max_length=45, unique=True)
    ordre_nivell = models.IntegerField(
        null=True,
        blank=True,
        help_text="S'utilitza per mostrar un nivell abans que un altre (Ex: ESO=0, CFSI=1000)",
    )
    descripcio_nivell = models.CharField(max_length=240, blank=True)
    anotacions_nivell = models.TextField(blank=True)
    matricula_oberta = models.BooleanField("Matrícula oberta", default=False)
    limit_matricula = models.DateField(
        "Límit matrícula",
        null=True,
        blank=True,
        help_text="Dia límit per fer confirmació de matrícula",
    )
    taxes = models.ForeignKey(
        "sortides.TipusQuota",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=None,
    )
    preexclusiva = models.BooleanField(
        "Matrícula exclusiva de Preinscripció", default=False
    )

    class Meta:
        abstract = True
        ordering = ["ordre_nivell"]
        verbose_name = "Nivell"
        verbose_name_plural = "Nivells"

    def __str__(self):
        return self.nom_nivell + " (" + self.descripcio_nivell + ")"

    def save(self, *args, **kwargs):
        super(AbstractNivell, self).save(
            *args, **kwargs
        )  # Call the "real" save() method.

    # amorilla@xtec.cat
    # Retorna el nivell que correspon segons CUSTOM_NIVELLS
    # Si no correspon cap aleshores retorna el nom_nivell original
    def getNivellCustom(self):
        for k, v in settings.CUSTOM_NIVELLS.items():
            if self.nom_nivell in v:
                return k
        return self.nom_nivell


class AbstractCurs(models.Model):
    nivell = models.ForeignKey("alumnes.Nivell", on_delete=models.CASCADE)
    nom_curs = models.CharField(
        "Nom curs", max_length=45, help_text="Un número que representa el curs (Ex: 3)"
    )
    nom_curs_complert = models.CharField(
        max_length=45,
        blank=True,
        unique=True,
        help_text="Dades que es mostraran (Ex: 1r ESO)",
    )
    data_inici_curs = models.DateField(
        "Comencen",
        null=True,
        blank=True,
        help_text="Dia que comencen les classes (cal informar aquest cap per poder fer control de presència)",
    )
    data_fi_curs = models.DateField(
        "Acaben",
        null=True,
        blank=True,
        help_text="Dia que finalitzen les classes (es poden posar dies festius a l'apartat corresponent)",
    )
    confirmacio_oberta = models.BooleanField("Confirmació activada", default=False)
    limit_confirmacio = models.DateField(
        "Límit confirmació",
        null=True,
        blank=True,
        help_text="Dia límit per fer confirmació de matrícula",
    )

    class Meta:
        abstract = True
        # order_with_respect_to = 'nivell'
        ordering = ["nivell", "nom_curs"]
        verbose_name = "Curs"
        verbose_name_plural = "Cursos"
        unique_together = (
            "nivell",
            "nom_curs",
        )

    def save(self, *args, **kwargs):
        super(AbstractCurs, self).save(
            *args, **kwargs
        )  # Call the "real" save() method.

    def __str__(self):
        return self.nom_curs_complert

    def dies(self):
        if not (self.data_inici_curs and self.data_fi_curs):
            return []
        import datetime as t

        totsElsDies = []
        dia = self.data_inici_curs
        while dia <= self.data_fi_curs:
            delta = t.timedelta(days=+1)
            dia += delta
            totsElsDies.append(dia)
        return totsElsDies


class AbstractGrup(models.Model):
    curs = models.ForeignKey("alumnes.Curs", on_delete=models.CASCADE)
    nom_grup = models.CharField(
        max_length=45, help_text="""Això normalment serà una lletra. Ex 'A' """
    )
    descripcio_grup = models.CharField(max_length=240, blank=True)

    class Meta:
        abstract = True
        ordering = ["curs", "curs__nivell__nom_nivell", "curs__nom_curs", "nom_grup"]
        verbose_name = "Grup"
        verbose_name_plural = "Grups"

    def __str__(self):
        return (
            self.descripcio_grup
            if self.descripcio_grup
            else self.curs.nom_curs_complert + " " + self.nom_grup
        )

    def save(self, *args, **kwargs):
        # descripció és una mena de cache.
        if not self.descripcio_grup:
            self.descripcio_grup = self.curs.nom_curs_complert + " " + self.nom_grup
        super(AbstractGrup, self).save(
            *args, **kwargs
        )  # Call the "real" save() method.


# ------------------------------------------------------------------------------------------------


# https://docs.djangoproject.com/en/dev/topics/db/managers/#django.db.models.Manager
# class AlumneManager(models.Manager):
#    def sincronitzaSaga(self,f, user):
#        import alumnes.sincronitzaSaga  as c
#        return c.sincronitza( f, user )

# ------------------------------------------------------------------------------------------------


class AbstractAlumne(models.Model):
    ESTAT_SINCRO_CHOICES = (
        ("PRC", "En procés de sincronització"),
        ("S-I", "Sincronitzat Insert"),
        ("S-U", "Sincronitzat Update"),
        ("DEL", "Alumne donat de baixa"),
        ("MAN", "Alumne donat d'alta manualment"),
    )
    PERIODICITAT_FALTES_CHOICES = (
        (0, "No notificar"),
        (1, "Un dia"),
        (2, "Dos dies"),
        (3, "Tres dies"),
        (7, "Una setmana"),
    )

    PERIODICITAT_INCIDENCIES_CHOICES = (
        (False, "No notificar."),
        (True, "Notificar-les totes."),
    )

    PRIMER_RESPONSABLE = (
        (0, "Responsable 1"),
        (1, "Responsable 2"),
    )

    ralc = models.CharField(max_length=100, blank=True, db_index=True)
    grup = models.ForeignKey("alumnes.Grup", on_delete=models.CASCADE)
    nom = models.CharField("Nom", max_length=240)
    nom_sentit = models.CharField(
        "Nom Sentit",
        max_length=240,
        blank=True,
        help_text="És el nom amb el que l'alumne se sent identificat "
        "tot i que formalment encara els tràmits de canvi de"
        " nom no estiguin completats",
    )
    cognoms = models.CharField("Cognoms", max_length=240)
    data_neixement = models.DateField("Data naixement", null=True)
    estat_sincronitzacio = models.CharField(
        choices=ESTAT_SINCRO_CHOICES, max_length=3, blank=True
    )

    # DEPRECATED vvv
    correu_tutors = models.CharField(max_length=240, blank=True)
    correu_relacio_familia_pare = models.EmailField(
        "1r Correu Notifi. Tutors",
        help_text="Correu de notificacions de un tutor",
        blank=True,
    )
    correu_relacio_familia_mare = models.EmailField(
        "2n Correu Notifi. Tutors",
        help_text="Correu de notificacions de l'altre tutor (opcional)",
        blank=True,
    )
    # DEPRECATED ^^^

    motiu_bloqueig = models.CharField(max_length=250, blank=True)

    # DEPRECATED vvv
    tutors_volen_rebre_correu = models.BooleanField(null=True)
    # DEPRECATED ^^^

    centre_de_procedencia = models.CharField(max_length=250, blank=True)
    localitat = models.CharField(max_length=240, blank=True)
    municipi = models.CharField(max_length=240, blank=True)
    cp = models.CharField(max_length=240, blank=True)
    # DEPRECATED vvv
    telefons = models.CharField(max_length=250, blank=True, db_index=True)
    tutors = models.CharField(max_length=250, blank=True)
    # DEPRECATED ^^^
    adreca = models.CharField(max_length=250, blank=True)
    correu = models.CharField(max_length=240, blank=True)

    # DEPRECATED vvv
    rp1_nom = models.CharField(max_length=250, blank=True)  # responsable 1
    rp1_telefon = models.CharField(max_length=250, blank=True, db_index=True)
    rp1_mobil = models.CharField(max_length=250, blank=True, db_index=True)
    rp1_correu = models.CharField(max_length=240, blank=True)
    rp2_nom = models.CharField(max_length=250, blank=True)  # responsable 2
    rp2_telefon = models.CharField(max_length=250, blank=True, db_index=True)
    rp2_mobil = models.CharField(max_length=250, blank=True, db_index=True)
    rp2_correu = models.CharField(max_length=240, blank=True)
    # DEPRECATED ^^^

    responsable_preferent = models.ForeignKey(
        "relacioFamilies.Responsable",
        null=True,
        on_delete=models.SET_NULL,
        help_text="Responsable preferent de l'alumne/a",
    )

    # DEPRECATED vvv
    primer_responsable = models.IntegerField(
        choices=PRIMER_RESPONSABLE,
        blank=False,
        default=0,
        help_text="Principal responsable de l'alumne/a",
    )
    # DEPRECATED ^^^

    altres_telefons = models.CharField(max_length=250, blank=True)

    data_alta = models.DateField(default=timezone.now, null=False)
    data_baixa = models.DateField(null=True, blank=True)

    user_associat = models.OneToOneField(
        AlumneUser,
        null=True,
        on_delete=models.SET_NULL,
    )

    usuaris_app_associats = models.ManyToManyField(
        User,
        through="usuaris.QRPortal",
        related_name="alumne_app_set",
        related_query_name="alumne_app",
    )
    # DEPRECATED vvv
    relacio_familia_darrera_notificacio = models.DateTimeField(null=True, blank=True)
    # DEPRECATED ^^^

    periodicitat_faltes = models.IntegerField(
        choices=PERIODICITAT_FALTES_CHOICES,
        blank=False,
        default=1,
        help_text="Interval de temps mínim entre dues notificacions",
    )

    periodicitat_incidencies = models.BooleanField(
        choices=PERIODICITAT_INCIDENCIES_CHOICES,
        blank=False,
        default=True,
        help_text="Periodicitat en la notificació de les incidències.",
    )

    foto = PrivateFileField(
        "Foto",
        upload_to="alumnes/fotos",
        content_types=CUSTOM_TIPUS_MIME_FOTOS,
        max_file_size=3145728,
        null=True,
        blank=True,
    )
    observacions = models.TextField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Informació visible pels seus professors/es",
    )

    aruco_marker = models.IntegerField(
        "Marker",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1022),
        ],
        help_text="Identificador del marker ARUCO associat a l'alumne. Ha de ser únic dins el nivell (Eso, Btx, ...) Del 0 al 99 per assignació manual",
    )

    class Meta:
        abstract = True
        ordering = ["grup", "cognoms", "nom"]
        verbose_name = "Alumne"
        verbose_name_plural = "Alumnes"
        # Constraints unique que no podem definir perquè els camps són d'altres taules:
        #   ("aruco_marker", "grup__curs__nivell"),  # l'aruco_marker ha de ser únic per nivell
        #   ("nom", "cognoms",  "data_neixement", "grup__curs__nivell"),("ralc","grup__curs__nivell"))

    def __str__(self):
        return ("És baixa: " if self.esBaixa() else "") + self.cognoms + ", " + self.nom

    def get_nom_sentit(self):
        return (
            ("És baixa: " if self.esBaixa() else "")
            + self.cognoms
            + ", "
            + (self.nom_sentit or self.nom)
        )

    def delete(self):
        self.data_baixa = datetime.today()
        self.save()

    def esBaixa(self):
        return self.data_baixa is not None

    def tutorsDeLAlumne(self):
        from django.db.models import Q

        q_tutors_individualitat = Q(tutorindividualitzat__alumne=self)
        q_tutors_grup = Q(tutor__grup=self.grup)
        return Professor.objects.filter(
            q_tutors_individualitat | q_tutors_grup
        ).distinct()

    def tutorsIndividualitzatsDeLAlumne(self):
        from django.db.models import Q

        q_tutors_individualitat = Q(tutorindividualitzat__alumne=self)
        return Professor.objects.filter(q_tutors_individualitat).distinct()

    def tutorsDelGrupDeLAlumne(self):
        return Professor.objects.filter(tutor__grup=self.grup).distinct()

    def tutorsDeLAlumne_display(self):
        return ", ".join([str(tutor) for tutor in self.tutorsDeLAlumne()])

    def force_delete(self):
        super(AbstractAlumne, self).delete()

    def esta_relacio_familia_actiu(self):
        # Si és major d'edat, no fa falta correus_relacio_familia
        TeCorreuResponsable = bool(
            self.get_correus_relacio_familia(checkMajorEdat=False)
        ) and any(self.responsablesActius())
        TeCorreuAlumne = (
            self.edat() >= 18
            and self.get_correu_relacio()
            and self.get_user_associat() is not None
            and self.user_associat.is_active
        )
        return TeCorreuResponsable or TeCorreuAlumne

    def responsablesActius(self):
        return [
            x.get_user_associat() is not None and x.user_associat.is_active
            for x in self.get_responsables()
            if x
        ]

    def get_correu_relacio(self):
        return self.correu

    def get_correus_relacio_familia(self, checkMajorEdat=True):
        emails = [
            x.correu_relacio_familia
            for x in self.get_responsables(compatible=True)
            if (x and x.correu_relacio_familia)
        ]
        if checkMajorEdat and self.edat() >= 18:
            emails.append(self.get_correu_relacio())
        return list(set(emails))

    def get_correus_tots(self):
        tots = self.get_correus_relacio_familia(checkMajorEdat=False)
        tots = tots + [
            x.correu for x in self.get_responsables(compatible=True) if x and x.correu
        ]
        tots = tots + [self.get_correu_relacio()]
        return list(set(tots))

    def get_telefons(self):
        return self.altres_telefons

    def get_user_associat(self):
        return self.user_associat if self.user_associat_id is not None else None

    def get_seguiment_tutorial(self):
        if not hasattr(self, "seguimenttutorial"):
            a = self
            try:
                seguiment = SeguimentTutorial.objects.get(
                    nom=a.nom,
                    cognoms=a.cognoms,
                    data_neixement=a.data_neixement,
                )
            except SeguimentTutorial.DoesNotExist:
                seguiment = SeguimentTutorial.objects.create(
                    nom=a.nom,
                    cognoms=a.cognoms,
                    datadarreraactualitzacio=datetime.now(),
                    data_neixement=a.data_neixement,
                    informacio_de_primaria="",
                    alumne=None,
                )
            seguiment.alumne = a
            seguiment.save()

            self.seguimenttutorial = seguiment

        return self.seguimenttutorial

    def cursa_obligatoria(self):
        return self.grup.curs.nivell not in Nivells_no_obligatoris()

    def cursa_nivell(self, nivell_txt):
        return Cursa_nivell(nivell_txt, self)

    # amorilla@xtec.cat
    # Retorna el nivell que correspon a l'alumne segons CUSTOM_NIVELLS
    # Si no correspon cap aleshores retorna el nivell assignat a la base de dades
    def getNivellCustom(self):
        for k, v in settings.CUSTOM_NIVELLS.items():
            if self.grup.curs.nivell.nom_nivell in v:
                return k
        return self.grup.curs.nivell.nom_nivell

    # amorilla@xtec.cat
    # Retorna l'edat de l'alumne.
    # Si s'indica una data per paràmetre retorna l'edat en la data indicada,
    # en altre cas calcula l'edat en el dia actual
    def edat(self, data=None):
        if data is None:
            data = date.today()
        dnaix = self.data_neixement
        return relativedelta(data, dnaix).years

    # amorilla@xtec.cat
    # Retorna true si és l'aniversari de l'alumne.
    # Té en compte el cas 29/2, si l'any no té 29/2 indica aniversari el 28/2.
    # Si s'indica una data per paràmetre retorna si és aniversari en la data indicada,
    # en altre cas calcula en el dia actual
    def aniversari(self, data=None):
        if data is None:
            data = date.today()
        dnaix = self.data_neixement
        return ((data.month, data.day) == (dnaix.month, dnaix.day)) or (
            not calendar.isleap(data.year)
            and (dnaix.month, dnaix.day) == (2, 29)
            and (data.month, data.day) == (2, 28)
        )

    @property
    def get_foto_or_default(self):
        foto = self.foto.url if self.foto else static("nofoto.png")
        return foto

    def get_responsables(self, rp1_dni=None, rp2_dni=None, compatible=False):
        """
        Retorna una tupla amb els dos responsables associats a l'alumne.
        - Si es passen DNIs, selecciona els responsables corresponents.
        - Si no es passen DNIs:
            - Retorna els responsables existents de l'alumne.
            #DEPRECATED vvv
            - Si no n'hi ha i 'compatible' és True, crea responsables
            temporals, per compatibilitat, segons les dades antigues del model alumne.
            #DEPRECATED ^^^
        """
        from django.apps import apps

        def crear_responsable_antic(
            nom_complet, correu, telefon1, telefon2, correu_familia
        ):
            if not (nom_complet or correu or telefon1 or telefon2 or correu_familia):
                return None
            nom, cognoms = ("", "")
            if "," in nom_complet:
                cognoms, nom = map(str.strip, nom_complet.split(",", 1))
            else:
                nom = nom_complet
            Responsable = apps.get_model("relacioFamilies", "Responsable")
            return Responsable(
                nom=nom,
                cognoms=cognoms,
                correu=correu,
                telefon=telefon1 or telefon2,
                correu_relacio_familia=correu_familia,
                periodicitat_faltes=self.periodicitat_faltes,
                periodicitat_incidencies=self.periodicitat_incidencies,
            )

        # Si no es passen DNIs
        if not rp1_dni and not rp2_dni:
            responsables = list(self.responsables.all())
            # DEPRECATED vvv
            # Compatibilitat antiga: crear responsables ficticis si no n'hi ha
            Responsable = apps.get_model("relacioFamilies", "Responsable")
            if not responsables and compatible and not Responsable.objects.exists():
                # Només crea uns responsables temporals si encara no s'ha fet la nova càrrega de
                # dades d'alumnes amb els responsables diferenciats (not Responsable.objects.exists())
                # Si ja s'ha fet la càrrega, i encara no té responsables associats, s'assumeix que es tracta
                # d'un alumne sense responsables.
                resp1 = crear_responsable_antic(
                    self.rp1_nom,
                    self.rp1_correu,
                    self.rp1_mobil,
                    self.rp1_telefon,
                    self.correu_relacio_familia_pare,
                )
                resp2 = crear_responsable_antic(
                    self.rp2_nom,
                    self.rp2_correu,
                    self.rp2_mobil,
                    self.rp2_telefon,
                    self.correu_relacio_familia_mare,
                )
                if self.primer_responsable == 1:
                    resp1, resp2 = resp2, resp1
                return resp1, resp2
            # DEPRECATED ^^^
            # Omple amb Nones si no s'arriba a 2 responsables
            while len(responsables) < 2:
                responsables.append(None)
            # Si hi ha un preferent i no està en primera posició, invertir l'ordre
            if (
                self.responsable_preferent
                and responsables[0] != self.responsable_preferent
                and responsables[1]
            ):
                responsables.reverse()
            return tuple(responsables)
        # Si es passen DNIs
        resp1 = self.responsables.filter(dni=rp1_dni).first()
        resp2 = self.responsables.filter(dni=rp2_dni).first()
        return resp1, resp2

    def get_telefons_responsables(self):
        return [
            x.get_telefon()
            for x in self.get_responsables(compatible=True)
            if x and x.get_telefon()
        ]

    def get_dades_responsables(self, responsable=None, nomesNoms=False):
        def dades_o_nom(resp, nomesNoms):
            if not resp:
                return ""
            return resp.get_nom() if nomesNoms else resp.get_dades()

        resp1, resp2 = self.get_responsables(compatible=True)
        if responsable is None:
            respPre = dades_o_nom(resp1, nomesNoms)
            respAlt = dades_o_nom(resp2, nomesNoms)
            return {"respPre": respPre, "respAlt": respAlt}
        # Amb responsable indicat
        respPre = dades_o_nom(resp1, False)
        respAlt = dades_o_nom(resp2, True)
        if responsable == resp2:
            respPre = dades_o_nom(resp2, False)
            respAlt = dades_o_nom(resp1, True)
        return {"respPre": respPre, "respAlt": respAlt}

    def esborraAntics_responsables(self, dnis):
        """
        Elimina altres responsables anteriors, només
        conserva els que corresponen a la llista de dnis.
        Els responsables sense alumnes queden com a baixa.
        dnis list amb els dnis vàlids de responsables
        """
        for r in self.responsables.exclude(dni__in=dnis):
            r.alumnes_associats.remove(self)
            if not r.alumnes_associats.exists():
                # Fa baixa si el responsable es queda sense alumnes
                r.delete()


class AbstractDadesAddicionalsAlumne(models.Model):
    alumne = models.ForeignKey("alumnes.Alumne", on_delete=models.CASCADE)
    label = models.CharField(max_length=50, help_text="Nom del camp addicional")
    value = models.CharField(
        max_length=500, blank=True, null=True, help_text="Contingut del camp addicional"
    )

    class Meta:
        abstract = True
        verbose_name = "Dada addicional de l'alumne"
        verbose_name_plural = "Dades addicionals dels alumnes"
        unique_together = ["alumne", "label"]

    def __str__(self):
        return (
            self.alumne.cognoms
            + ", "
            + self.alumne.nom
            + " - "
            + self.label
            + ": "
            + self.value
        )
