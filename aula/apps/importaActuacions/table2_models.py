# -*- encoding: utf-8 -*-
import django_tables2 as tables
from django_tables2.utils import A

from aula.apps.tutoria.models import Actuacio


class Table2_llista_actuacions(tables.Table):

    id_actuacio = tables.TemplateColumn(
                        template_code = u"""{{record.id}}""", 
                        order_by=( '-id',  )
                        )
    
    moment_actuacio = tables.TemplateColumn(
                        template_code = u"""{{record.moment_actuacio}}""", 
                        order_by=( '-moment_actuacio',  )
                        )
    
    alumne  = tables.TemplateColumn(
                        template_code = u"""{{ record.alumne }}""", 
                        order_by=( 'alumne.cognoms', 'alumne.nom', '-moment_actuacio',   )
                        )
    
    
    qui = tables.TemplateColumn(
                        template_code = u"""{{ record.professional }} ( {{record.get_qui_fa_actuacio_display}})""", 
                        order_by=( 'professional', '-moment_actuacio',  ),
                        verbose_name=u"Qui?"
                        )
    
    actuacio  = tables.TemplateColumn(
                        template_code = u"""{{ record.actuacio }}""",
                        orderable = False 
                        )
    
    class Meta:
        model = Actuacio
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("id_actuacio", "moment_actuacio", "alumne", "qui", "actuacio", )
        fields = sequence
        template = 'bootable2.html' 