# -*- encoding: utf-8 -*-
import django_tables2 as tables
from django_tables2.utils import A

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from aula.apps.incidencies.models import Expulsio
from aula.apps.incidencies.models import TipusIncidencia

class Table2_ExpulsioTramitar(tables.Table):

    antiguitat = tables.TemplateColumn(
                        template_code = u"""{{ record.getDate|timesince }}""", 
                        order_by=( '-dia_expulsio', '-franja_expulsio.hora_inici' )
                        )
    
    alumne = tables.TemplateColumn(
                        template_code = u"""<a href="/tutoria/detallTutoriaAlumne/{{record.alumne.pk}}/all/">{{ record.alumne }}</a> ( {{ record.alumne.grup  }} )""", 
                        order_by=( 'alumne.cognoms', 'alumne.nom'),
                        verbose_name=u"Alumne Expulsat:"
                        )

    professor = tables.TemplateColumn(
                        template_code = u"""{{ record.professor }}""", 
                        order_by=( 'professor.last_name', 'professor.fist_name'),
                        verbose_name=u"Expulsat per:"
                        )



    
    class Meta:
        model = Expulsio
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("alumne", "professor" )
        fields = sequence
        template = 'bootable2.html' 
        

class Table2_AlertesAcumulacioExpulsions(tables.Table):
    alumne = tables.TemplateColumn(
                                   template_code = u"""<a href="/tutoria/detallTutoriaAlumne/{{record.pk}}/all/">{{ record }}</a>""", 
                                   order_by=( 'cognoms', 'nom'),
                                   verbose_name=u"Alumne"
                                   )

    grup = tables.TemplateColumn(
                                   template_code = u"""{{ record.grup  }}""", 
                                   order_by=( 'grup.descripcio_grup', 'cognoms', 'nom'),
                                   verbose_name=u"Grup"
                                   )

    expulsions = tables.TemplateColumn(
                                       template_code = u"""<a href="/tutoria/detallTutoriaAlumne/{{record.pk}}/incidencies">{{record.nExpulsions}}</a>""", 
                                       order_by="-nExpulsionsSort",
                                       verbose_name=u"Expulsions"
                                       )

    incidenciesAula = tables.TemplateColumn(
                                            template_code = u"""<a href="/tutoria/detallTutoriaAlumne/{{record.pk}}/incidencies">{{record.nIncidenciesAula}}</a>""", 
                                            order_by="-nIncidenciesAulaSort",
                                            verbose_name=u"Inc. a l'aula"
                                            )

    incidenciesForaAula = tables.TemplateColumn(
                                                template_code = u"""<a href="/tutoria/detallTutoriaAlumne/{{record.pk}}/incidencies">{{record.nIncidenciesForaAula}}</a>""",
                                                order_by='-nIncidenciesForaAulaSort',
                                                verbose_name=u"Inc. fora de l'aula"
                                                )

    expulsionsAndIncidencies= tables.TemplateColumn(
                                                template_code = u"""<a href="/tutoria/detallTutoriaAlumne/{{record.pk}}/incidencies">{{record.nExpAndInc}}</a>""",
                                                order_by='-nExpAndInc',
                                                verbose_name=u"Exp+Inc"
                                                )

    sancionar = tables.TemplateColumn(
                        template_code = u"""<a href=\'javascript:confirmAction(\"/incidencies/sancio/{{record.pk}}\", \"Segur que vols sancionar a {{record}}?\")\'>sancionar...</a>""", 
                        verbose_name = " ",
                        orderable = False,
                        )

    # Columne oculta, utilitzada per a ordenar
    incidencies = tables.TemplateColumn(
                          "{{record.incidencies}}",
                          order_by='-incidencies',
                          verbose_name = u"Incidències totals",
                          visible=False
                          )
    
    class Meta:
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("alumne", "grup", "expulsions", "incidenciesAula", "incidenciesForaAula", "expulsionsAndIncidencies", "sancionar")
        fields = sequence
        order_by = ("expulsions", "incidenciesAula", "incidenciesForaAula" )
        template = 'bootable2.html'

