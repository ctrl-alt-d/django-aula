# This Python file uses the following encoding: utf-8
from django.db import models
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.usuaris.models import Departament, Professor
from aula.apps.usuaris.tools import set_notificacio, set_revisio, get_notif_revisio
from aula.apps.sortides.business_rules.sortida import clean_sortida
from aula.apps.alumnes.models import Alumne
from django.apps import apps
from django.db.models import Q
from six import python_2_unicode_compatible
from django.conf import settings

from aula.utils.tools import unicode
import django.utils.timezone


class TPV(models.Model):
    # nom és la clau, es reserva el nom "centre" per identificar el TPV principal
    nom = models.CharField("Nom", max_length=32, unique=True)
    codi = models.CharField("Codi Comerç", max_length=32)
    key = models.CharField("Key", max_length=64)
    descripcio = models.CharField("Descripció", max_length=200)
    entornReal = models.BooleanField("Fa servir entorn real", default=False)

    class Meta:
        verbose_name = "TPV"
        verbose_name_plural = "TPVs"

    def __str__(self):
        return self.descripcio


@python_2_unicode_compatible
class Sortida(models.Model):

    TIPUS_ACTIVITAT_CHOICES = [("A", "Activitat"), ("P", "Pagament")]

    SUBTIPUS_ACTIVITAT = {
        "A": [
            ("S", "Sortida"),
            ("X", "Xerrada"),
            ("T", "Taller"),
            ("A", "Altres"),
        ],
        "P": [
            ("D", "Dossier"),
            ("M", "Material"),
            ("A", "Matrícula"),
            ("P", "Pagament parcial"),
        ],
    }
    SUBTIPUS_ACTIVITAT_CHOICES = []
    for clau in SUBTIPUS_ACTIVITAT:
        for value in SUBTIPUS_ACTIVITAT[clau]:
            SUBTIPUS_ACTIVITAT_CHOICES.append((clau + value[0], value[1]))

    CONSELL_ESCOLAR_CHOICES = (
        ("P", "Pendent"),
        ("A", "Aprovada"),
        ("R", "Rebutjada"),
        ("N", "No necessita aprovació"),
    )

    TIPUS_TRANSPORT_CHOICES = (
        (
            "TR",
            "Tren",
        ),
        (
            "BU",
            "Bus",
        ),
        (
            "AP",
            "A peu",
        ),
        (
            "CO",
            "Combinat",
        ),
        (
            "ND",
            "No cal desplaçament",
        ),
        (
            "MP",
            "Mitjans propis",
        ),
    )

    ESTAT_CHOICES = (
        (
            "E",
            "Esborrany",
        ),
        (
            "P",
            "Proposat/da",
        ),
        (
            "R",
            "Revisat/da pel Coordinador",
        ),
        (
            "G",
            "Gestionat/da pel Cap d'estudis",
        ),
    )

    TIPUS_PAGAMENT_CHOICES = [
        (
            "NO",
            "No cal pagament",
        ),
        (
            "EF",
            "En efectiu",
        ),
        (
            "ON",
            "Online a través del djAu",
        ),
        (
            "EB",
            """Al caixer de l'entitat bancària""",
        ),
    ]

    NO_SINCRONITZADA = "N"
    SINCRONITZANT_SE = "x"
    YES_SINCRONITZADA = "Y"
    ESTAT_SYNC_CHOICES = (
        (NO_SINCRONITZADA, "No sincronitzada"),
        (SINCRONITZANT_SE, ""),
        (YES_SINCRONITZADA, ""),
    )

    estat = models.CharField(
        max_length=1,
        default="E",
        choices=ESTAT_CHOICES,
        help_text="Estat de l'activitat. No es considera proposta d'activitat fins que no passa a estat 'Proposada'",
    )

    estat_sincronitzacio = models.CharField(
        max_length=1,
        default=NO_SINCRONITZADA,
        choices=ESTAT_SYNC_CHOICES,
        editable=False,
        help_text="Per passar els alumnes a 'no han de ser a l'aula' ",
    )

    tipus = models.CharField(
        max_length=1,
        default="A",
        choices=TIPUS_ACTIVITAT_CHOICES,
        help_text="Tipus d'activitat",
    )

    subtipus = models.CharField(
        max_length=2,
        default="AS",
        choices=SUBTIPUS_ACTIVITAT_CHOICES,
        help_text="Subtipus d'activitat",
    )

    titol = models.CharField(
        max_length=40,
        help_text="Escriu un títol breu que serveixi per identificar aquesta activitat.Ex: exemples: Visita al Museu Dalí, Ruta al barri gòtic, Xerrada sobre drogues ",
    )

    ambit = models.CharField(
        "Àmbit",
        max_length=20,
        help_text="Quins alumnes hi van? Ex: 1r i 2n ESO. Ex: 1r ESO A.",
    )

    ciutat = models.CharField(
        "Lloc",
        max_length=30,
        help_text="On es fa l'activitat. Ex. Sala polivalent, Aula 201, Teatre el Jardí, Barcelona,,...",
    )

    esta_aprovada_pel_consell_escolar = models.CharField(
        "Aprovada_pel_consell_escolar?",
        max_length=1,
        choices=CONSELL_ESCOLAR_CHOICES,
        default="P",
        help_text="Marca si aquesta activitat ja ha estat aprovada pel consell escolar",
    )

    departament_que_organitza = models.ForeignKey(
        Departament,
        help_text="Indica quin departament organitza l'activitat",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    comentari_organitza = models.CharField(
        max_length=50,
        help_text="En cas de no ser organitzat per un departament cal informar qui organitza l'activitat.",
        blank=True,
    )

    alumnes_a_l_aula_amb_professor_titular = models.BooleanField(
        "Passar llista com normalment?",
        default=False,
        help_text="Els alumnes seran a l'aula i el professor de l'hora corresponent passarà llista com fa habitualment.",
    )
    data_inici = models.DateField(
        "Afecta classes: Des de",
        help_text="Primer dia lectiu afectat per l'activitat",
        blank=True,
        null=True,
    )
    franja_inici = models.ForeignKey(
        FranjaHoraria,
        verbose_name="Afecta classes: Des de franja",
        related_name="hora_inici_sortida",
        help_text="Primera franja lectiva afectada per l'activitat",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    data_fi = models.DateField(
        "Afecta classes: Fins a",
        help_text="Darrer dia  lectiu de l'activitat",
        blank=True,
        null=True,
    )
    franja_fi = models.ForeignKey(
        FranjaHoraria,
        verbose_name="Afecta classes: fins a franja",
        related_name="hora_fi_sortida",
        help_text="Darrera franja lectiva afectatada per l'activitat",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    calendari_desde = models.DateTimeField(
        "Horari real, des de:",
        help_text="Horari real de l'activitat, hora de sortida, aquest horari, a més, es publicarà al calendari del Centre",
    )
    calendari_finsa = models.DateTimeField(
        "Horari real, fins a:",
        help_text="Horari real de l'activitat, hora de tornada, aquest horari, a més, es publicarà al calendari del Centre",
    )

    calendari_public = models.BooleanField(
        "Publicar activitat",
        default=True,
        help_text="Ha d'apareixer al calendari públic de la web",
    )

    materia = models.CharField(
        max_length=50,
        help_text="Matèria que es treballa a l'activitat. Escriu el nom complet.",
    )

    tipus_de_pagament = models.CharField(
        max_length=2,
        choices=TIPUS_PAGAMENT_CHOICES,
        help_text="Quin serà el tipus de pagament predominant",
        default="NO",
        null=False,
    )

    preu_per_alumne = models.DecimalField(
        max_digits=5,
        blank=True,
        null=True,
        decimal_places=2,
        help_text="Preu per alumne. Indica el preu que apareixerà a l'autorització ( el posa secretaria / coordinador(a) activitats )",
    )

    codi_de_barres = models.CharField(
        "Codi de barres pagament",
        blank=True,
        default="",
        max_length=100,
        help_text="Codi de barres pagament caixer ( el posa secretaria / coordinador(a) activitats )",
    )

    informacio_pagament = models.TextField(
        "Informació pagament",
        blank=True,
        default="",
        help_text="Instruccions de pagament: entitat, concepte, import, ... ( el posa secretaria / coordinador(a) activitats )",
    )

    termini_pagament = models.DateTimeField(
        "Termini pagament",
        blank=True,
        null=True,
        help_text="Omplir si hi ha data límit per a realitzar el pagament.",
    )

    programa_de_la_sortida = models.TextField(
        verbose_name="Descripció de l'activitat",
        help_text="Aquesta informació arriba a les famílies. Descriu l'activitat incloent altres informacions d'interès (desenvolupament, tipus d'activitat, horaris, objectius, ...)",
    )

    condicions_generals = models.TextField(
        blank=True,
        help_text="Aquesta informació arriba a les famílies. Indica què cal portar (boli, llibreta, portàtil,...), recomanacions (crema solar, gorra, insecticida, ...),  menjar i beguda,...  Si no cal portar res cal indicar-ho.",
    )

    participacio = models.CharField(
        "Participació",
        editable=False,
        default="N/A",
        max_length=100,
        help_text="Nombre d’alumnes participants sobre el total possible. Per exemple: 46 de 60",
    )

    mitja_de_transport = models.CharField(
        max_length=2,
        choices=TIPUS_TRANSPORT_CHOICES,
        help_text="Tria el mitjà de transport",
    )

    empresa_de_transport = models.CharField(
        max_length=250,
        blank=True,
        default="",
        help_text="Indica el nom de l'empresa de transports i número de contracte/pressupost.",
    )

    pagament_a_empresa_de_transport = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Indica la quantitat que ha de pagar l'institut pel lloguer del bus, o compra de bitllets. Si no ha de pagar res indica-ho, escriu 'res'.",
    )

    pagament_a_altres_empreses = models.TextField(
        blank=True,
        default="",
        help_text="Indica la quantitat, l'empresa que ha de rebre els diners, el sistema de pagament, el número de contracte i el termini. Si no s'ha de pagar res indica-ho, escriu 'res'.",
    )

    feina_per_als_alumnes_aula = models.TextField(
        blank=True,
        default="",
        help_text="Descriu o comenta on els professors trobaran la feina que han de fer els alumnes que es quedin a l'aula. Si no queden alumnes a l'aula indica-ho.",
    )

    comentaris_interns = models.TextField(
        blank=True,
        help_text="Espai per anotar allò que sigui rellevant de cares a l'activitat. Si no hi ha comentaris rellevants indica-ho.",
    )

    professor_que_proposa = models.ForeignKey(
        Professor,
        editable=False,
        help_text="Professor que proposa l'activitat",
        related_name="professor_proposa_sortida",
        on_delete=models.CASCADE,
    )

    professors_responsables = models.ManyToManyField(
        Professor,
        blank=True,
        verbose_name="Professors que organitzen",
        help_text="Professors responsables de l'activitat",
        related_name="professors_responsables_sortida",
    )

    altres_professors_acompanyants = models.ManyToManyField(
        Professor,
        verbose_name="Professors acompanyants",
        help_text="Professors acompanyants",
        blank=True,
    )

    tutors_alumnes_convocats = models.ManyToManyField(
        Professor,
        editable=False,
        verbose_name="Tutors dels alumnes",
        help_text="Tutors dels alumnes",
        blank=True,
        related_name="tutors_sortida",
    )

    alumnes_convocats = models.ManyToManyField(
        Alumne,
        blank=True,
        help_text="Alumnes convocats. Per seleccionar un grup sencer, clica una sola vegada damunt el nom del grup.",
        related_name="sortides_confirmades",
    )

    alumnes_que_no_vindran = models.ManyToManyField(
        Alumne,
        blank=True,
        help_text="Alumnes que haurien d'assistir-hi perquè estan convocats però sabem que no venen.",
        related_name="sortides_on_ha_faltat",
    )

    alumnes_justificacio = models.ManyToManyField(
        Alumne,
        blank=True,
        help_text="Alumnes que no venen i disposen de justificació per no assistir al Centre el dia de l'activitat.",
        related_name="sortides_falta_justificat",
    )

    pagaments = models.ManyToManyField(Alumne, through="Pagament")

    # Per futures ampliacions, de moment no es fa servir.
    # Totes les sortides es paguen amb el TPV per defecte.
    tpv = models.ForeignKey(TPV, on_delete=models.PROTECT, null=True)

    @property
    def n_acompanyants(self):
        return self.altres_professors_acompanyants.count()

    @property
    def nom_acompanyants(self):
        nom_acompanyants = ", ".join(
            [unicode(u) for u in self.altres_professors_acompanyants.all()]
        )
        n_acompanyants = self.altres_professors_acompanyants.count()
        txt_acompanyants = (
            "({0}) {1}".format(n_acompanyants, nom_acompanyants)
            if n_acompanyants
            else "Sense acompanyants"
        )
        return txt_acompanyants

    def clean(self):
        clean_sortida(self)

    def __str__(self):
        return self.titol

    @staticmethod
    def alumne_te_sortida_en_data(alumne, dia, franja):
        Sortida = apps.get_model("sortides", "Sortida")

        # auxiliar: tornen el mateix dia?
        q_mateix_dia = Q(data_inici=dia, data_fi=dia)

        # condicio 1 ( no tornen el mateix dia )
        q_entre_dates = Q(data_inici__lt=dia, data_fi__gt=dia)
        q_primer_dia = Q(
            data_inici=dia, franja_inici__hora_inici__lte=franja.hora_inici
        )
        q_darrer_dia = Q(data_fi=dia, franja_fi__hora_inici__gte=franja.hora_inici)
        q_c1 = ~q_mateix_dia & (q_entre_dates | q_primer_dia | q_darrer_dia)

        # condicio 2 ( tornen el mateix dia )
        q_entre_hores = Q(
            franja_inici__hora_inici__lte=franja.hora_inici,
            franja_fi__hora_inici__gte=franja.hora_inici,
        )
        q_c2 = q_mateix_dia & q_entre_hores

        # condicio 3 ( estat de la sortida revisada o gestionada )
        q_revisada = Q(estat="R")
        q_gestionada = Q(estat="G")

        sortides_de_laulumne = set(
            alumne.sortides_confirmades.values_list("id", flat=True)
        )
        sortides_de_laulumne_no_hi_va = set(
            alumne.sortides_on_ha_faltat.values_list("id", flat=True)
        )
        sortides = sortides_de_laulumne - sortides_de_laulumne_no_hi_va

        resultat = (
            Sortida.objects.filter(id__in=sortides)
            .filter(q_c1 | q_c2)
            .filter(q_revisada | q_gestionada)
            .all()
        )

        # print 'revisant {0} {1} {2} sortides: {3}'.format( alumne, dia, franja, resultat)

        return resultat


class TipusQuota(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "Tipus de quota"
        verbose_name_plural = "Tipus de quotes"

    def __str__(self):
        return self.nom


def return_any_actual():
    return django.utils.timezone.now().year


class Quota(models.Model):
    from aula.apps.alumnes.models import Curs

    importQuota = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    dataLimit = models.DateField(null=True, blank=True)
    any = models.IntegerField(
        help_text="Correspon a l'any on comença el curs. Ex. curs any1/any2, seria any1.",
        default=return_any_actual,
    )
    descripcio = models.CharField(max_length=200)
    #  Si no s'indica curs, serveix per a tots els alumnes
    curs = models.ForeignKey(Curs, on_delete=models.PROTECT, null=True, blank=True)
    tpv = models.ForeignKey(TPV, on_delete=models.PROTECT)
    tipus = models.ForeignKey(TipusQuota, on_delete=models.PROTECT)

    class Meta:
        ordering = ["any", "curs__nom_curs_complert"]
        verbose_name = "Quota"
        verbose_name_plural = "Quotes"

    def __str__(self):
        return (
            str(self.importQuota)
            + " "
            + str(self.curs)
            + " "
            + str(self.any)
            + " "
            + self.descripcio
            if self.descripcio
            else self.tipus
        )

    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()
        # Comprova que l'any no sigui del futur
        if self.any > return_any_actual():
            raise ValidationError(
                "No es poden crear quotes del curs indicat fins al {0}.".format(
                    self.any
                )
            )
        # Comprova si existeix una quota del mateix tipus, curs i any.
        if self.tipus.nom in [
            settings.CUSTOM_TIPUS_QUOTA_MATRICULA,
            "taxcurs",
            "uf",
        ]:
            q = Quota.objects.exclude(id=self.id).filter(
                tipus=self.tipus, curs=self.curs, any=self.any, tpv=self.tpv
            )
            # Si hi ha una altra, error
            if q:
                raise ValidationError(
                    "Ja existeix una Quota de tipus {0} per aquest curs i any.".format(
                        self.tipus.nom
                    )
                )


class QuotaCentreManager(models.Manager):
    def get_queryset(self):
        #  Només quotes del TPV 'centre'
        return super(QuotaCentreManager, self).get_queryset().filter(tpv__nom="centre")


class QuotaCentre(Quota):
    objects = QuotaCentreManager()

    class Meta:
        proxy = True

    def __str__(self):
        return (
            str(self.importQuota)
            + " "
            + str(self.curs)
            + " "
            + str(self.any)
            + " "
            + self.descripcio
            if self.descripcio
            else self.tipus
        )


@python_2_unicode_compatible
class Pagament(models.Model):
    # Pagament per a una sortida o una quota
    alumne = models.ForeignKey(Alumne, on_delete=models.PROTECT, null=True)
    sortida = models.ForeignKey(Sortida, on_delete=models.PROTECT, null=True)
    data_hora_pagament = models.DateTimeField(null=True)
    pagament_realitzat = models.BooleanField(null=True, default=False)
    ordre_pagament = models.CharField(max_length=12, unique=True, null=True)
    quota = models.ForeignKey(Quota, on_delete=models.PROTECT, null=True)
    # Si es fracciona es fa en dos pagaments, només per quotes
    fracciona = models.BooleanField(null=True, default=False)
    # import d'aquesta fracció,  si fraccionat
    importParcial = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    # data límit d'aquesta fracció
    dataLimit = models.DateField(null=True)
    observacions = models.CharField(max_length=150, null=True, blank=True)
    """
    estat del pagament:
        '' Pagament no iniciat.
        'E' Error. Pagament rebujat per redsys.
        'T' Transmès. Pagament iniciat, però no finalitzat. Es deixa un temps per completar-ho.
        'F' Finalitzat. Pagament correctament finalitzat.
    """
    estat = models.CharField(max_length=1, blank=True, null=True, default="")
    notificacions_familia = models.ManyToManyField("usuaris.NotifUsuari", db_index=True)

    def __str__(self):
        return "Pagament realitzat per l'alumne {}: {}".format(
            self.alumne,
            self.pagament_realitzat if self.pagament_realitzat else "No indicat",
        )

    @property
    def pagamentFet(self):
        return (
            self.pagament_realitzat
            or (self.quota and self.quota.importQuota == 0)
            or (self.sortida and self.sortida.preu_per_alumne == 0)
        )

    @property
    def importReal(self):
        return (
            self.importParcial
            if self.fracciona
            else (
                self.quota.importQuota
                if self.quota
                else self.sortida.preu_per_alumne if self.sortida else 0
            )
        )

    @property
    def getdataLimit(self):
        return (
            self.dataLimit
            if self.fracciona or self.dataLimit
            else (
                self.quota.dataLimit
                if self.quota
                else self.sortida.termini_pagament if self.sortida else ""
            )
        )

    def set_notificacio(self, notificacio):
        set_notificacio(self, notificacio)

    def set_revisio(self, revisio):
        set_revisio(self, revisio)

    def get_notif_revisio(self, usuari, fmt_data=None):
        """
        Retorna str, str amb notificació, revisió de l'usuari
        """
        return get_notif_revisio(self, usuari, fmt_data)


class QuotaPagamentManager(models.Manager):
    def get_queryset(self):
        #  Pagaments referents a una quota. Els pagaments en estat 'E' són pagaments cancel·lats.
        return (
            super(QuotaPagamentManager, self)
            .get_queryset()
            .filter(quota__isnull=False)
            .exclude(estat="E")
        )


class QuotaPagament(Pagament):
    objects = QuotaPagamentManager()

    class Meta:
        proxy = True

    def __str__(self):
        if self.fracciona:
            return "Pagament parcial {} de la quota {} {}, de l'alumne {}: {}".format(
                self.importParcial,
                self.quota.descripcio,
                self.quota.importQuota,
                self.alumne,
                "Fet" if self.pagament_realitzat else "Pendent",
            )
        return "Pagament de la quota {} {}, de l'alumne {}: {}".format(
            self.quota.descripcio,
            self.quota.importQuota,
            self.alumne,
            "Fet" if self.pagament_realitzat else "Pendent",
        )


class SortidaPagamentManager(models.Manager):
    def get_queryset(self):
        #  Pagaments referents a una sortida. Els pagaments en estat 'E' són pagaments cancel·lats.
        return (
            super(SortidaPagamentManager, self)
            .get_queryset()
            .filter(sortida__isnull=False)
            .exclude(estat="E")
        )


class SortidaPagament(Pagament):
    objects = SortidaPagamentManager()

    class Meta:
        proxy = True

    def __str__(self):
        return "Pagament de la sortida {}, realitzat per l'alumne {}: {}".format(
            self.sortida,
            self.alumne,
            self.pagament_realitzat if self.pagament_realitzat else "No indicat",
        )


@python_2_unicode_compatible
class NotificaSortida(models.Model):
    alumne = models.ForeignKey(Alumne, on_delete=models.CASCADE)
    sortida = models.ForeignKey(Sortida, on_delete=models.CASCADE)

    # DEPRECATED vvv
    relacio_familia_revisada = models.DateTimeField(null=True)
    relacio_familia_notificada = models.DateTimeField(null=True)
    # DEPRECATED ^^^

    notificacions_familia = models.ManyToManyField("usuaris.NotifUsuari", db_index=True)

    def __str__(self):
        return "{} {}".format(self.alumne, self.sortida)

    def set_notificacio(self, notificacio):
        set_notificacio(self, notificacio)

    def set_revisio(self, revisio):
        set_revisio(self, revisio)

    def get_notif_revisio(self, usuari, fmt_data=None):
        """
        Retorna str, str amb notificació, revisió de l'usuari
        """
        return get_notif_revisio(self, usuari, fmt_data)


# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #
from django.db.models.signals import m2m_changed, pre_save  # noqa: E402

from aula.apps.sortides.business_rules.sortida import sortida_m2m_changed  # noqa: E402

m2m_changed.connect(sortida_m2m_changed, sender=Sortida.alumnes_convocats.through)
m2m_changed.connect(sortida_m2m_changed, sender=Sortida.alumnes_que_no_vindran.through)
m2m_changed.connect(sortida_m2m_changed, sender=Sortida.alumnes_justificacio.through)
m2m_changed.connect(sortida_m2m_changed, sender=Sortida.professors_responsables.through)
m2m_changed.connect(
    sortida_m2m_changed, sender=Sortida.altres_professors_acompanyants.through
)

# QuotaPagament
from aula.apps.sortides.business_rules.quotapagament import (  # noqa: E402
    quotapagament_pre_save,
)

pre_save.connect(quotapagament_pre_save, sender=QuotaPagament)
