import django_tables2 as tables

class HorariAlumneTable(tables.Table):
    Ara = tables.TemplateColumn(
                        verbose_name='#',
                        template_code=u"""
                        {% if record.es_hora_actual %}
                        ->
                        {% endif %}
                        """,
                        orderable=False,
                        )
    Hora = tables.TemplateColumn(
                        template_code = u"""
                        {{ record.hora }}
                        """,
                        orderable = False,
                        )
    Horari_Alumne = tables.TemplateColumn(
                        template_code = u"""
                        {% if record.no_ha_de_ser_a_laula %}
                        {{ record.missatge_no_ha_de_ser_a_laula }}
                        {% else %}
                        {{ record.horari_alumne | linebreaksbr}} 
                        {% endif %}
                        """,
                        orderable = False,
                        )
    Horari_Grup = tables.TemplateColumn(
                        template_code=u"""
                        {{ record.horari_grup | linebreaksbr}} 
                        """,
                        orderable=False,
                        )

    class Meta:
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        template = 'bootable2.html'

