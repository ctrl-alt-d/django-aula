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


class Table2_IncidenciesMostrar(tables.Table):
    Ara = tables.TemplateColumn(
        template_code=u"""
                            {% if record.es_hora_actual %}
                            ->
                            {% endif %}
                            """,
        orderable=False,
    )

    class Meta:
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        template = 'bootable2.html'


class Table2_ExpulsionsPendentsTramitar(tables.Table):
    Alumne = tables.TemplateColumn(
                        template_code=u"""
                                    <a style='color:red' 
                                    href="/incidencies/editaExpulsio/{{ record.pk }}/"> {{ record.alumne }} </a>
                                    """,
                        orderable=False,
                        )
    Dia = tables.TemplateColumn(
                        template_code=u"""
                                    {{ record.dia_expulsio }}
                                    """,
                        orderable=False,
                        )
    Hora = tables.TemplateColumn(
                        template_code=u"""
                                    {{ record.franja_expulsio }}
                                    """,
                        orderable=False,
                        )
    Motiu = tables.TemplateColumn(
                        template_code=u"""
                                    {{ record.motiu }}
                                    """,
                        orderable=False,
    )
    Assignatura = tables.TemplateColumn(
                        template_code=u"""
                                    {{ record.control_assistencia.impartir.horari.assignatura }}
                                    """,
                        orderable=False,
    )

    class Meta:
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        template = 'bootable2.html'



class Table2_ExpulsionsPendentsPerAcumulacio(tables.Table):
    Alumne = tables.TemplateColumn(
                        template_code=u"""
                                     {{ record.alumne }} 
                                    """,
                        orderable=False,
    )
    Generar = tables.TemplateColumn(
        attrs={'th': {'width': '50%'}},
        verbose_name = " ",
        template_code=u"""
                                        <a style='color:red' 
                                        href="/incidencies/posaExpulsioPerAcumulacio/{{ record.pk }}"> Generar expulsió </a>
                                        """,
        orderable=False,
    )

    class Meta:
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        template = 'bootable2.html'


class Table2_ExpulsionsIIncidenciesPerAlumne(tables.Table):

    Eliminar = tables.TemplateColumn(
        verbose_name=u" ",
        attrs={'th': {'width': '4%'}},
        template_code=u"""
                                                {% if not record.es_incidencia_d_aula and not record.dia_expulsio %} 
                                                        <a style="color:red" href="/incidencies/eliminaIncidencia/{{record.pk}}"> 
                                                            <span class="glyphicon glyphicon-remove"/> 
                                                        </a>
                                                {% endif %}
                                                {% if record.dia_expulsio %}
                                                    <a href="/incidencies/editaExpulsio/{{ record.pk }}/"> 
                                                            <span class="glyphicon glyphicon-pencil"/> 
                                                    </a>
                                                {% endif %}
                                                {% if record.es_incidencia_d_aula %}
                                                    <a class= "gi-2x" href="/incidencies/posaIncidenciaAula/{{record.control_assistencia.impartir.pk}}"> 
                                                            <span class="glyphicon glyphicon-eye-open"/> 
                                                    </a>

                                                {% endif %}
                                                """,
        orderable=False,
    )

    Tipus = tables.TemplateColumn(
        verbose_name=u" ",
        attrs={'th': {'width': '10%'}},
        template_code=u"""
                                        {% if record.dia_incidencia %}
                                            {{ record.tipus }} 
                                        {% else %}
                                            Expulsió
                                        {% endif %}
                                        {% if record.es_vigent %} <br>(vigent) {% endif %}
                                        """,
        orderable=False,
    )
    DataAsignatura = tables.TemplateColumn(
        verbose_name=u" ",
        attrs={'th': {'width': '35%'}},
        #verbose_name=u"Data/Assignatura",
        template_code=u"""
                                            {{ record.dia_expulsio }} {{ record.franja_expulsio }} {{ record.get_estat_display }}
                                            {{ record.dia_incidencia }}
                                            {{ record.franja_incidencia }}
                                            {{ record.control_assistencia.impartir.horari.assignatura}} <br>
                                            {{ record.get_gestionada_pel_tutor_motiu_display }}
                                            """,
        orderable=False,
    )
    Motiu = tables.TemplateColumn(
        verbose_name=u" ",
        #attrs={'th': {'width': '46%'}},
        template_code=u"""
                                            {{record.mini_motiu}}
                                            {{record.descripcio_incidencia}}
                                            """,
        orderable=False,
    )


    class Meta:
        # add class="paleblue" to <table> tag
        show_header = False
        attrs = {"class": "paleblue table table-striped"}
        template = 'bootable2.html'