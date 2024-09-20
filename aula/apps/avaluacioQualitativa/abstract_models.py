# This Python file uses the following encoding: utf-8

from django.db import models


class AbstractItemQualitativa(models.Model):
    codi_agrupacio = models.CharField(
        "Codi agrupació",
        max_length=10,
        blank=True,
        null=False,
        help_text="Codi per facilitar l'entrada de la qualitativa. No apareix a l'informe a les famílies.",
    )
    text = models.CharField(
        "Item de la Qualitativa",
        max_length=120,
        unique=True,
        null=False,
        help_text="Important: No canvieu mai el significat d'una frase! Canviarieu els resultats de l'avaulació.",
    )
    nivells = models.ManyToManyField(
        "alumnes.Nivell", help_text="Tria els nivells on aquesta frase pot aparèixer."
    )

    class Meta:
        abstract = True
        ordering = ["codi_agrupacio", "text"]
        verbose_name = "Frase aval. qualitativa"
        verbose_name_plural = "Frases aval. qualitativa"

    def __str__(self):
        return "{0}.-{1}".format(self.codi_agrupacio, self.text)


class AbstractAvaluacioQualitativa(models.Model):
    nom_avaluacio = models.CharField(
        "Avaluació Qualitativa",
        max_length=120,
        unique=True,
        null=False,
        help_text="Ex: Avaluació qualitativa 1ra Avaluació",
    )
    data_obrir_avaluacio = models.DateField(
        "Primer dia per entrar Qualitativa",
        null=False,
        help_text="Data a partir de la qual els professors podran entrar l'avaluació.",
    )
    data_tancar_avaluacio = models.DateField(
        "Darrer dia per entrar Qualitativa",
        null=False,
        help_text="Darrer dia que tenen els professors per entrar la Qualitativa.",
    )
    grups = models.ManyToManyField(
        "alumnes.Grup", help_text="Tria els grups a avaluar."
    )
    data_obrir_portal_families = models.DateField(
        "Primer dia per veure els resultats al portal famílies",
        null=True,
        blank=True,
        help_text="Els pares podran veure els resultats al portal famílies a partir de la data aquí introduïda.",
    )
    data_tancar_tancar_portal_families = models.DateField(
        "Darrer dia per veure els resultats al portal famílies",
        null=True,
        blank=True,
        help_text="Els pares podran veure els resultats al portal famílies fins a la data aquí introduïda.",
    )

    class Meta:
        abstract = True
        ordering = ["data_obrir_avaluacio"]
        verbose_name = "Avaluació Qualitativa"
        verbose_name_plural = "Avaluacions Qualitatives"

    def __str__(self):
        return self.nom_avaluacio


class AbstractRespostaAvaluacioQualitativa(models.Model):
    qualitativa = models.ForeignKey(
        "avaluacioQualitativa.AvaluacioQualitativa", on_delete=models.CASCADE
    )
    alumne = models.ForeignKey("alumnes.Alumne", on_delete=models.CASCADE)
    professor = models.ForeignKey("usuaris.Professor", on_delete=models.CASCADE)
    assignatura = models.ForeignKey(
        "assignatures.Assignatura", on_delete=models.CASCADE
    )
    item = models.ForeignKey(
        "avaluacioQualitativa.ItemQualitativa",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    frase_oberta = models.CharField(
        "Frase oberta", max_length=120, help_text="Frase oberta", blank=True
    )

    relacio_familia_revisada = models.DateTimeField(null=True, editable=False)
    relacio_familia_notificada = models.DateTimeField(null=True, editable=False)

    class Meta:
        abstract = True
        ordering = ["qualitativa", "assignatura", "alumne"]
        verbose_name = "Resposta aval. Qualitativa"
        verbose_name_plural = "Respostes aval. Qualitative"
        unique_together = (
            "qualitativa",
            "assignatura",
            "alumne",
            "professor",
            "item",
        )

    def get_resposta_display(self):
        if hasattr(self, "item") and self.item is not None:
            return self.item.text
        else:
            return self.frase_oberta
