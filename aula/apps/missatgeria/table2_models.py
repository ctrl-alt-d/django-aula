# This Python file uses the following encoding: utf-8

import django_tables2 as tables
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaksbr
from django.utils.safestring import mark_safe

from aula.apps.missatgeria.missatges_a_usuaris import MISSATGES
from django.template.defaulttags import register

from aula.apps.alumnes.models import Alumne

class MissatgesTable(tables.Table):
    Data = tables.TemplateColumn(
        attrs={'th': {'width': '25%'}},
        template_code=u"""
                            {% now "jS F Y H:i" as ara %} 
                            {% if record.moment_lectura|date:"jS F Y H:i" == ara %}
                                <span class="blink_me text-danger"> <strong> Nou-> </strong></span>
                            {% endif %}
                            <span class="gi-2x">
                            {% if record.importancia == "PI" %}
                                <span class="mybtn-blue glyphicon glyphicon-info-sign"/>
                            {% elif record.importancia == "VI" %}
                                <span class="mybtn-red glyphicon glyphicon-exclamation-sign"/>
                            {% else %}
                                <span class="mybtn-orange glyphicon glyphicon-warning-sign"/>
                            {% endif %}
                            </span>
                            <span class="gi-1x">
                                <span class="text-{%Missatges_content record.missatge.tipus_de_missatge%}">
                                    {{record.missatge.data|date:"j F Y H:i"}}
                                </span>
                            </span>
                            """,
        orderable=False,
    )

    Remitent = tables.TemplateColumn(
        template_code=u"""
                                """,
        orderable=False,
    )


    def render_Remitent(self,record):
        if record.missatge.remitent.groups.filter( name = 'alumne' ).exists():
            alumne = get_object_or_404(Alumne, user_associat=record.missatge.remitent)
            return u"Missatge des del portal famílies de: {alumne} ({tutors})".format( alumne=alumne,
                                                                                       tutors = alumne.tutorsDeLAlumne_display() )
        else:
            try:
                missatge_class = list(MISSATGES[record.missatge.tipus_de_missatge].keys())[0]
            except:
                missatge_class = 'dark'
            missatge='<span class="text-' + missatge_class + '">'
            if record.missatge.remitent.last_name:
                missatge = missatge + record.missatge.remitent.first_name + ' ' + record.missatge.remitent.last_name
                if record.missatge.remitent.email:
                    missatge = missatge + '\n' + record.missatge.remitent.email
            else:
                missatge = missatge + record.missatge.remitent.username
            missatge = missatge + '</span>'
            return mark_safe(missatge)

    @register.simple_tag
    def Missatges_content(key):
        try:
            return list(MISSATGES[key].keys())[0]
        except:
            return 'dark'

    Contingut = tables.TemplateColumn(
        attrs={'th': {'width': '60%'}},
        template_code=u"""  
                                    <div class="text-{%Missatges_content record.missatge.tipus_de_missatge%}">
                                        {{record.missatge.text_missatge|linebreaks}}
                                        {% if record.missatge.errors %}
                                        <ul>
                                            {% for txt in record.missatge.errors %}
                                            <li>{{ txt|escape }}</li>
                                            {% endfor %}
                                        </ul>
                                        {% endif %}
                                        {% if record.missatge.warnings %}
                                        <ul>
                                            {% for txt in record.missatge.warnings %}
                                            <li>{{ txt|escape }}</li>
                                            {% endfor %}
                                        </ul>
                                        {% endif %}
                                        {% if record.missatge.infos %}
                                        <ul>
                                            {% for txt in record.missatge.infos %}
                                            <li>{{ txt|escape }}</li>
                                            {% endfor %}
                                        </ul>
                                        {% endif %}
                                    </div>
                                    """,
        orderable=False,
    )
    Seguit = tables.TemplateColumn(
        verbose_name=" ",
        template_code=u"""
                                    {% if record.missatge.enllac %}
                                        <a  href="/missatgeria/llegeix/{{record.pk}}"> 
                                             {% if record.followed %}
                                                  <span class="glyphicon glyphicon-eye-open"/>
                                             {% else %}
                                                  <span class="glyphicon glyphicon-eye-close"/>
                                             {% endif %}
                                        </a>
                                    {% endif %}
                                    """,
        orderable=False,
    )

    class Meta:
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        template = 'bootable2.html'

