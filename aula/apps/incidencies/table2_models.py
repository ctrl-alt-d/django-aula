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
                        template_code = u"""<a href="/tutoria/detallTutoriaAlumne/{{record.alumne.pk}}/all/">{{ record.alumne }}</a> ( {{ record.alumne.grup  }} )""", 
                        order_by=( 'alumne.cognoms', 'alumne.nom'),
                        verbose_name=u"Alumne Expulsat:"
                        )

    professor = tables.TemplateColumn(
                        template_code = u"""{{ record.professor }}""", 
                        order_by=( 'professor.last_name', 'professor.fist_name'),
                        verbose_name=u"Expulsat per:"
                        )



    
    class Meta:
        model = Expulsio
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("alumne", "professor" )
        fields = sequence
        template = 'bootable2.html' 
        
        