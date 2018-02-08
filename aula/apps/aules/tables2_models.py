import django_tables2 as tables


class HorariAulaTable(tables.Table):
    Hora = tables.TemplateColumn(
        verbose_name='',
        template_code=u"""
                        {{record.franja}}
                        """,
        orderable=False,
    )

    Reserves = tables.TemplateColumn(
        attrs={'th': {'width': '60%'}},
        template_code=u"""
                        <div class="progress">
                        {% if record.reserva %}
                            {% if not aula.horari_lliure %}
                                <div class="progress-bar progress-bar-danger" style="width: 100%">
                                {{record.professor}}-{{record.assignatura}}-{{record.grup}}
                              </div>                            
                            {% else %}
                              <div class="progress-bar progress-bar-success" style="width: 35%">
                              </div>
                              <div class="progress-bar progress-bar-danger" style="width: 65%">
                              {{record.professor}}-{{record.assignatura}}-{{record.grup}}
                              </div>  
                            {% endif %}                       
                        {% else %}
                              <div class="progress-bar progress-bar-success" style="width: 100%">
                              </div>
                        {% endif %}
                        </div>
                        """,
        orderable=False,
    )
    Reservar = tables.TemplateColumn(
        verbose_name='',
        template_code=u"""
                        <span class="gi-2x">
                        {% if aula.reservable and not record.reserva %}
                            <a href="/aules/tramitarReservaAula/{{aula.pk}}/{{record.franja.pk}}/{{dia.year}}/{{dia.month}}/{{dia.day}}/">
                            <span class="mybtn-green glyphicon glyphicon-plus-sign"> </span> <br />
                            </a>
                        {% endif %}
                        </span>
                        """,

    )

    class Meta:
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        template = 'bootable2.html'

