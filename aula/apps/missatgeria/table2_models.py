import django_tables2 as tables
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import linebreaksbr

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
                                <span class="mybtn-green glyphicon glyphicon-info-sign"/>
                            {% elif record.importancia == "VI" %}
                                <span class="mybtn-red glyphicon glyphicon-exclamation-sign"/>
                            {% else %}
                                <span class="mybtn-orange glyphicon glyphicon-warning-sign"/>
                            {% endif %}
                            </span>
                            <span class="gi-1x">
                            {{record.missatge.data|date:"j F Y H:i"}}
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
        if record.missatge.remitent.groups.filter( name = 'alumnes' ).exists():
            alumne = get_object_or_404(Alumne, user_associat=record.missatge.remitent)
            return u"Alumne: {alumne} ({tutors})".format( alumne=alumne, tutors = alumne.tutorsDeLAlumne_display() )
        else:
            missatge=''
            if record.missatge.remitent.last_name:
              missatge = record.missatge.remitent.first_name + ' ' + record.missatge.remitent.last_name
              if record.missatge.remitent.email:
                  missatge = missatge + '\n' + record.missatge.remitent.email
            else:
                missatge = record.missatge.remitent.username
            return missatge



    Contingut = tables.TemplateColumn(
       attrs={'th': {'width': '60%'}},
        template_code=u"""
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

