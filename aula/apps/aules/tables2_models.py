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
        attrs={'th': {'width': '50%'}},
        template_code=u"""
        
                        <div class="progress">
                        {% if record.reserva %}
                            {% if not aula.horari_lliure %}         
                              <div id="popoverData" rel="popover" data-placement="top" 
                                    data-original-title="Motiu: {{record.reserva.motiu}}" 
                                    data-content="Materia: {{record.assignatura}} - Grup: {{record.grup}}"
                                    data-trigger="hover" class="progress-bar progress-bar-danger" 
                                    role="progressbar"  style="width: 100%">
                                <span>{{record.professor}}</span>       
                              </div>                           
                            {% else %}
                              <div class="progress-bar progress-bar-success" style="width: 50%"></div>
                              <div id="popoverData" rel="popover" data-placement="top" 
                              data-original-title="Motiu: {{record.reserva.motiu}}" 
                              data-content={{record.assignatura}}-{{record.grup}} 
                              data-trigger="hover" class="progress-bar progress-bar-danger" 
                              role="progressbar"  style="width: 50%">
                                <span>{{record.professor}}</span>       
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

