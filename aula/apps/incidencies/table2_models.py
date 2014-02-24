# -*- encoding: utf-8 -*-
import django_tables2 as tables
from django_tables2.utils import A

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from aula.apps.incidencies.models import Expulsio

class Table2_ExpulsioTramitar(tables.Table):

    antiguitat = tables.TemplateColumn(
                        template_code = u"""{{ record.getDate|timesince }}""", 
                        order_by=( '-dia_expulsio', '-franja_expulsio.hora_inici' )
                        )
    
    alumne = tables.TemplateColumn(
                        template_code = u"""{{ record.alumne }} ( {{ record.alumne.grup  }} )""", 
                        order_by=( 'alumne.cognoms', 'alumne.nom')
                        )

    total_expulsions_vigents = tables.TemplateColumn(
                        template_code = u"""{{ record.totalExpulsionsVigents }}""", 
                        order_by=( '-totalExpulsionsVigents' )
                        )


    
    class Meta:
        model = Expulsio
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("alumne", )
        fields = sequence
        template = 'bootable2.html' 