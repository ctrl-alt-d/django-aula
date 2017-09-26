import django_tables2 as tables


class HorariAlumneTable(tables.Table):
    hora = tables.TemplateColumn(
                        template_code = u"""
                        {% if record.es_hora_actual %}<b>{% endif %}
                        {{ record.hora }}
                        {% if record.es_hora_actual %}</b>{% endif %}
                        """, 
                        orderable = False,
                        )
    aula = tables.Column(orderable = False,)
    professor = tables.Column(orderable = False,)
    assignatura = tables.Column(orderable = False,)
    class Meta:
         # add class="paleblue" to <table> tag
         attrs = {"class": "paleblue table table-striped"}
         template = 'bootable2.html'

