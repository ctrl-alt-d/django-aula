# -*- encoding: utf-8 -*-
import django_tables2 as tables
from aula.apps.aules.models import ReservaAula

class HorariAulaTable(tables.Table):
    Hora = tables.TemplateColumn(
        verbose_name='',
        template_code=u"""
                        {{record.franja}}
                        """,
        orderable=False,
    )

    Reserves = tables.TemplateColumn(
        attrs={'th': {'width': '80%'}},
        template_code=u"""
        
                        <div class="progress">
                        {% if record.reserva %}
                            {% if not aula.horari_lliure %}         
                                <span class="progress-bar progress-bar-danger popoverData" rel="popover" data-placement="top" 
                                    data-original-title="Motiu: {{record.reserva.motiu}}" 
                                    {% if record.assignatura %} 
                                        data-content="Materia: {{record.assignatura}} - Grup: {{record.grup}}"
                                    {% endif %}
                                    data-trigger="hover" 
                                    role="progressbar"  style="width: 100%">{{record.professor}}</span>                        
                            {% else %}
                              <!-- <div class="progress-bar progress-bar-success" style="width: 50%"></div>
                              <div id="popoverData" rel="popover" data-placement="top" 
                              data-original-title="Motiu: {{record.reserva.motiu}}" 
                              data-content={{record.assignatura}}-{{record.grup}} 
                              data-trigger="hover" class="progress-bar progress-bar-danger" 
                              role="progressbar"  style="width: 50%">
                                <span>{{record.professor}}</span>       
                              </div>  -->
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
                            {% if record.reservable %}
                                <a href="/aules/tramitarReservaAula/{{aula.pk}}/{{record.franja.pk}}/{{dia.year}}/{{dia.month}}/{{dia.day}}/">
                                <span class="mybtn-green glyphicon glyphicon-plus-sign"> </span> <br />
                                </a>
                            {% endif %}
                            {% if record.eliminable %}
                                <a href='javascript:confirmAction("/aules/eliminarReservaAula/{{record.reserva.pk}}/{{aula.pk}}/{{dia.year}}/{{dia.month}}/{{dia.day}}" ,  
                                                                  " {{ "Segur que vols anul·lar la reserva de l'aula"|escapejs}} {{record.reserva.aula.nom_aula}} {{"hora:"}} {{record.reserva.hora}}?")'>
                                    <span class="mybtn-red glyphicon glyphicon-minus-sign"> </span> <br />           
                                </a>
                            {% endif %}
                        </span>
                        """,

    )

    class Meta:
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        template = 'bootable2.html'




class Table2_ReservaAula(tables.Table):

    es_del_passat =  tables.TemplateColumn(
                                    template_code = u"""
                                        {% if record.es_del_passat %} 
                                                    <span class="glyphicon glyphicon-calendar"/> 
                                        {% endif %}
                                        """,
                                    verbose_name = "",
                                    orderable = False,
                     )

    class Meta:
        model = ReservaAula
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("es_del_passat", "dia_reserva", "hora", "aula", "motiu" )
        fields = sequence
        template = 'bootable2.html' 
