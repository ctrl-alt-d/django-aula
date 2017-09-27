import django_tables2 as tables

class HorariAlumneTable(tables.Table):
    hora = tables.TemplateColumn(
                        template_code = u"""
                        {% if record.es_horari_grup %}<span style ="color:#999999">{% endif %}
                        {% if record.es_hora_actual %}<b>{% endif %}
                        {{ record.hora }}
                        {% if record.es_hora_actual %}</b>{% endif %}
                        {% if record.es_horari_grup %}</span>{% endif %}
                        """, 
                        orderable = False,
                        )
    aula = tables.TemplateColumn(
                        template_code=u"""
                        {% if record.es_horari_grup %} <span style ="color:#999999">{% endif %}
                        {% if record.es_hora_actual %} <b> {% endif %}
                        {{ record.aula }}
                        {% if record.es_hora_actual %} </b> {% endif %}
                        {% if record.es_horari_grup %} </span>{% endif %}
                        """,
                        orderable = False,
                        )
    professor = tables.TemplateColumn(
                        template_code=u"""
                        {% if record.es_horari_grup %} <span style ="color:#999999">{% endif %}
                        {% if record.es_hora_actual %} <b> {% endif %}
                        {{ record.professor }}
                        {% if record.es_hora_actual %} </b> {% endif %}
                        {% if record.es_horari_grup %} </span>{% endif %}
                        """,
                        orderable = False,
                        )
    assignatura = tables.TemplateColumn(
                        template_code=u"""
                        {% if record.es_horari_grup %} <span style ="color:#999999">{% endif %}
                        {% if record.es_hora_actual %} <b> {% endif %}
                        {{ record.assignatura }}
                        {% if record.es_hora_actual %} </b> {% endif %}
                        {% if record.es_horari_grup %} </span>{% endif %}
                        """,
                        orderable = False,
                        )
    class Meta:
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        template = 'bootable2.html'

