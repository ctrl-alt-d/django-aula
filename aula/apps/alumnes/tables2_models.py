import django_tables2 as tables


class HorariAlumneTable(tables.Table):
    hora = tables.TemplateColumn(
                        template_code = u"""
                        {% if record.es_hora_actual %}<b>{% endif %}
                        {{ record.hora }}
                        {% if record.es_hora_actual %}</b>{% endif %}
                        """, 
                        order_by=( 'hora' )
                        )
    aula = tables.Column()
    professor = tables.Column()
    assignatura = tables.Column()
    class Meta:
         # add class="paleblue" to <table> tag
         attrs = {"class": "paleblue table table-striped"}
         template = 'bootable2.html'

