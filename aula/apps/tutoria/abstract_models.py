# This Python file uses the following encoding: utf-8

from django.db import models
from django.template.defaultfilters import date


class AbstractSeguimentTutorial(models.Model):
    alumne = models.OneToOneField("alumnes.Alumne", null=True, on_delete=models.CASCADE)
    nom = models.CharField(max_length=240)
    cognoms = models.CharField(max_length=240)
    datadarreraactualitzacio = models.DateTimeField(null=True, blank=True)
    data_neixement = models.DateField()
    informacio_de_primaria = models.TextField(blank=True)

    class Meta:
        abstract = True
        verbose_name = "Capçalera seguiment tutorial"
        verbose_name_plural = "Capçaleres seguiment tutorial"
        unique_together = ("nom", "cognoms", "data_neixement")


class AbstractResumAnualAlumne(models.Model):
    seguiment_tutorial = models.ForeignKey(
        "tutoria.SeguimentTutorial", on_delete=models.CASCADE
    )
    curs_any_inici = models.IntegerField()
    text_resum = models.TextField(blank=True)

    class Meta:
        abstract = True
        verbose_name = "Resum Anual Alumne"
        verbose_name_plural = "Resums Anuals Alumnes"


class AbstractSeguimentTutorialPreguntes(models.Model):
    pregunta = models.CharField(max_length=250, unique=True)
    ajuda_pregunta = models.CharField(max_length=250, blank=True)
    es_pregunta_oberta = models.BooleanField()
    possibles_respostes = models.TextField(blank=True)

    class Meta:
        abstract = True
        verbose_name = "Pregunta seguiment tutorial"
        verbose_name_plural = "Preguntes seguiment tutorial"


class AbstractSeguimentTutorialRespostes(models.Model):
    seguiment_tutorial = models.ForeignKey(
        "tutoria.SeguimentTutorial", on_delete=models.CASCADE
    )
    any_curs_academic = models.IntegerField()
    pregunta = models.CharField(max_length=250)
    resposta = models.TextField()
    ordre = models.IntegerField(default=100)
    professorQueInforma = models.CharField(
        max_length=200, null=False, blank=True, default=""
    )

    class Meta:
        abstract = True
        unique_together = ("seguiment_tutorial", "any_curs_academic", "pregunta")
        verbose_name = "Resposta de seguiment tutorial"
        verbose_name_plural = "Respostes de seguiment tutorial"


# ----------------------------------------------------------------------------------------------------------


class AbstractActuacio(models.Model):
    QUI_CHOICES = (
        (
            "T",
            """Tutor/a""",
        ),
        (
            "O",
            """Cotutor/a""",
        ),
        (
            "C",
            """Cap d'estudis""",
        ),
        (
            "E",
            """Equip psicop.""",
        ),
        (
            "A",
            """Altres""",
        ),
    )
    AMB_QUI_CHOICES = (
        (
            "A",
            """Alumne""",
        ),
        (
            "F",
            """Familia""",
        ),
        (
            "T",
            """Altres""",
        ),
    )
    ASSUMPTE_CHOICES = (
        (
            "T",
            """Tutoria individualitzada""",
        ),
        (
            "C",
            """(PSI) Conflicte comportament""",
        ),
        (
            "V",
            """(PSI) Valoració""",
        ),
        (
            "S",
            """(PSI) Seguiment""",
        ),
        (
            "O",
            """(PSI) Orientació acadèmica""",
        ),
        (
            "E",
            """(PSI) Suport educatiu""",
        ),
        (
            "G",
            """(PSI) Gestió de les emocions""",
        ),
        (
            "I",
            """(PSI) Gestió social""",
        ),
        (
            "P",
            """(PSI) Pla individualitzat""",
        ),
        (
            "A",
            """Actuació puntual""",
        ),
        (
            "F",
            """Entrevista Família""",
        ),
    )
    alumne = models.ForeignKey(
        "alumnes.Alumne",
        help_text="Alumne sobre el qual es fa l'actuació",
        db_index=True,
        on_delete=models.CASCADE,
    )
    professional = models.ForeignKey(
        "usuaris.Professional",
        null=True,
        blank=True,
        help_text="Professional que fa l'actuacio",
        db_index=True,
        on_delete=models.CASCADE,
    )
    moment_actuacio = models.DateTimeField(
        help_text="Data i Hora de l'actuació. Format: 2011-06-01 9:05"
    )
    qui_fa_actuacio = models.CharField(
        choices=QUI_CHOICES, max_length=1, help_text="Qui realitza l'actuació"
    )
    amb_qui_es_actuacio = models.CharField(
        choices=AMB_QUI_CHOICES,
        max_length=1,
        help_text="Sobre qui es realitza l'actuació",
    )
    assumpte = models.CharField(
        choices=ASSUMPTE_CHOICES, max_length=1, help_text="Assumpte"
    )
    actuacio = models.TextField(
        blank=True,
        help_text="Explicació detallada de l'actuació realitzada. No inclogueu dades mèdiques ni diagnòstiques.",
    )

    class Meta:
        abstract = True
        verbose_name = "Actuació"
        verbose_name_plural = "Actuacions"


class AbstractTutor(models.Model):
    professor = models.ForeignKey("usuaris.Professor", on_delete=models.CASCADE)
    grup = models.ForeignKey("alumnes.Grup", on_delete=models.CASCADE)

    def __str__(self):
        return "{professor} tutoritza {grup}".format(
            professor=self.professor, grup=self.grup
        )

    class Meta:
        abstract = True
        verbose_name = "Entrada taula Tutors"
        verbose_name_plural = "Entrades taula Tutors"
        unique_together = (("professor", "grup"),)


class AbstractTutorIndividualitzat(models.Model):
    professor = models.ForeignKey("usuaris.Professor", on_delete=models.CASCADE)
    alumne = models.ForeignKey("alumnes.Alumne", on_delete=models.CASCADE)

    class Meta:
        abstract = True
        verbose_name = "Entrada Tutors Individualitzats"
        verbose_name_plural = "Entrades Tutors Individualitzats"
        unique_together = (("professor", "alumne"),)


# ----------------------------------------------------------


class AbstractCartaAbsentisme(models.Model):
    alumne = models.ForeignKey(
        to="alumnes.Alumne", verbose_name="Alumne", on_delete=models.CASCADE
    )
    carta_numero = models.IntegerField(editable=False, verbose_name="Avís número")
    tipus_carta = models.CharField(editable=False, max_length=10)
    faltes_fins_a_data = models.DateField(
        editable=False, verbose_name="Faltes fins a data"
    )
    # amorilla@xtec.cat  per a poder mostrar la data 'des de' a les cartes
    faltes_des_de_data = models.DateField(
        editable=False, verbose_name="Faltes des de data", blank=True, null=True
    )
    professor = models.ForeignKey(
        to="usuaris.Professor",
        verbose_name="Professor que signa la carta",
        on_delete=models.CASCADE,
    )
    data_carta = models.DateField(verbose_name="Data de la carta", null=True)
    faltes_incloses = models.TextField(
        editable=False, blank=True, verbose_name="Faltes incloses a la carta"
    )
    carta_esborrada_moment = models.DateTimeField(editable=False, blank=True, null=True)
    nfaltes = models.IntegerField(
        editable=False, verbose_name="Absències injustificades"
    )
    impresa = models.BooleanField(editable=False, default=False)

    class Meta:
        abstract = True
        ordering = ["alumne", "carta_numero"]

    def __str__(self):
        return "Carta núm {0} ({1}) de {2}".format(
            self.carta_numero, date(self.data_carta, "j N"), self.alumne
        )
