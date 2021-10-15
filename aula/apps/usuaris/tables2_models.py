import django_tables2 as tables


class HorariProfessorTable(tables.Table):
    Ara = tables.TemplateColumn(
                        verbose_name='#',
                        template_code=u"""
                        {% now "H:i" as ara %}
                        {% if ara > record.horari.hora.hora_inici|date:"H:i" and ara < record.horari.hora.hora_fi|date:"H:i" %}
                            <span class="blink_me text-danger"> <strong> -> </strong></span>
                        {% endif %}
                        """,
                        orderable=False,
                        )
    Hora = tables.TemplateColumn(
                        template_code = u"""
                        {{ record.horari.hora }}
                        """,
                        orderable = False,
                        )
    Assignatura = tables.TemplateColumn(
        template_code=u"""
                        {{ record.horari.assignatura.getLongName}}
                        """,
        orderable=False,
    )
    Grup = tables.TemplateColumn(
        template_code=u"""
                        {% if record.horari.grup %}
                            {{ record.horari.grup }}
                        {% else %}
                            --
                        {% endif %}     
                         """,
        orderable=False,
    )
    Aula = tables.TemplateColumn(
                        template_code = u"""
                            {{ record.get_nom_aula }}
                        """,
                        orderable = False,
                        )
    class Meta:
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        template = 'bootable2.html'

