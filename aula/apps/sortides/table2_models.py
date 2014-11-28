# -*- encoding: utf-8 -*-
import django_tables2 as tables
from django_tables2.utils import A

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from aula.apps.sortides.models import Sortida

class Table2_Sortides(tables.Table):
    
    titol_de_la_sortida = tables.LinkColumn('sortides__sortides__edit_by_pk', kwargs={'pk': A('pk'),})
    
    class Meta:
        model = Sortida
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("estat", "tipus", "titol_de_la_sortida", "ambit", "data_inici", "professor_que_proposa", "professor_responsable", )
        fields = sequence
        template = 'bootable2.html' 

class Table2_SortidesGestio(tables.Table):
    
    titol_de_la_sortida = tables.LinkColumn('sortides__sortides__editGestio_by_pk', kwargs={'pk': A('pk'),})
    
    class Meta:
        model = Sortida
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("estat", "tipus", "titol_de_la_sortida", "ambit", "data_inici", "professor_que_proposa", "professor_responsable", )
        fields = sequence
        template = 'bootable2.html'         