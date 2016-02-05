# -*- encoding: utf-8 -*-
import django_tables2 as tables
from django_tables2.utils import A

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from aula.apps.tutoria.models import Actuacio


class Table2_Actuacions(tables.Table):
    
    moment_actuacio = tables.TemplateColumn(
                        template_code = u"""{{record.moment_actuacio}} ( fa {{ record.getDate|timesince }} )""", 
                        order_by=( '-moment_actuacio',  )
                        )
    
    grup = tables.TemplateColumn(
                        template_code = u"""{{ record.alumne.grup }}""", 
                        order_by=( 'record.alumne.grup', 'record.alumne.cognoms', 'record.alumne.nom' )
                        )
    
    alumne  = tables.TemplateColumn(
                        template_code = u"""{{ record.alumne }}""", 
                        order_by=( 'record.alumne.cognoms', 'record.alumne.nom'  )
                        )
    
    
    qui = tables.TemplateColumn(
                        template_code = u"""{{ record.professional }} ( {{record.get_qui_fa_actuacio_display}})""", 
                        order_by=( 'record.professional' ),
                        verbose_name=u"Qui?"
                        )
    
    ambqui = tables.TemplateColumn(
                        template_code = u"""{{ record.get_amb_qui_es_actuacio_display }}""", 
                        order_by=( 'record.amb_qui_es_actuacio', 'record.alumne.grup', 'record.alumne.cognoms', 'record.alumne.nom' ),
                        verbose_name=u"Amb qui?"
                        )
    
    assumpte  = tables.TemplateColumn(
                        template_code = u"""{{ record.assumpte }}""", 
                        order_by=( 'record.assumpte', 'record.alumne.grup', 'record.alumne.cognoms', 'record.alumne.nom' )
                        )
    
    accions= tables.TemplateColumn( template_code=u"""
                    <div class="btn-group btn-group-xs">
                        <a class="btn dropdown-toggle btn-primary btn-xs" data-toggle="dropdown" href="#">
                          Accions
                          <span class="caret"></span>
                        </a>
                        <ul class="dropdown-menu pull-right dropdown-menu-right">
                        
                          <li>
                            <a href="/tutoria/editaActuacio/{{record.pk}}">
                            Modificar/Veure dades<br>
                            </a>
                          </li>
                        
                          <li>
                            <a href="/tutoria/esborraActuacio/{{record.pk}}">
                            Esborra actuació<br>
                            </a>
                          </li>

                        </ul>
                      </div>
            """
            , orderable = False, )
    
    class Meta:
        model = Actuacio
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("moment_actuacio", "grup", "alumne", "qui", "ambqui", "assumpte", )
        fields = sequence
        template = 'bootable2.html' 
        