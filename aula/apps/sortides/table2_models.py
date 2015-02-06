# -*- encoding: utf-8 -*-
import django_tables2 as tables
from django_tables2.utils import A

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from aula.apps.sortides.models import Sortida

class Table2_Sortides(tables.Table):
    
    titol_de_la_sortida = tables.LinkColumn('sortides__sortides__edit_by_pk', kwargs={'pk': A('pk'),})
    
    accions = tables.TemplateColumn( u"""
                <div class="btn-group btn-group-xs">
                    <a class="btn dropdown-toggle btn-primary btn-xs" data-toggle="dropdown" href="#">
                      Accions
                      <span class="caret"></span>
                    </a>
                    <ul class="dropdown-menu">
                    
                      <li>
                        <a href="/sortides/sortidaEdit/{{record.id}}">
                        Modificar dades<br>
                        </a>
                      </li>
                    
                      <li>
                        <a href="/sortides/alumnesConvocats/{{record.id}}">
                        Gestionar alumnes convocats<br>
                        </a>
                      </li>
                    
                      <li>
                        <a href="/sortides/alumnesFallen/{{record.id}}">
                        Gestionar alumnes que faltaran<br>
                        </a>
                      </li>
                    
                      <li>
                        <a href="/sortides/professorsAcompanyants/{{record.id}}">
                        Professors acompanyants<br>
                        </a>
                      </li>
                    
                      <li>
                        <a href='javascript:confirmAction("/sortides/esborrar/{{record.id}}"  , "Segur que vols esborrar l'activitat {{record.titol_de_la_sortida}} ?")'>
                        Esborrar<br>
                        </a>
                      </li>
                    
                    </ul>
                  </div>
    """,
    orderable = False,)
    
    participacio = tables.Column ( orderable = False,)
    n_acompanyants = tables.Column ( orderable = False,)
    
    class Meta:
        model = Sortida
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("estat", "tipus", "titol_de_la_sortida", "ambit", "calendari_desde", "professor_que_proposa", "participacio" , "n_acompanyants" )
        fields = sequence
        template = 'bootable2.html' 

class Table2_SortidesGestio(tables.Table):
    
    titol_de_la_sortida = tables.LinkColumn('sortides__sortides__editGestio_by_pk', kwargs={'pk': A('pk'),})
    participacio = tables.Column ( orderable = False,)
    accions = tables.TemplateColumn( u"""
                <div class="btn-group btn-group-xs">
                    <a class="btn dropdown-toggle btn-primary btn-xs" data-toggle="dropdown" href="#">
                      Accions
                      <span class="caret"></span>
                    </a>
                    <ul class="dropdown-menu">
                    
                      <li>
                        <a href="/sortides/sortidaEditGestio/{{record.id}}">
                        Modificar dades<br>
                        </a>
                      </li>
                    
                      <li>
                        <a href="/sortides/alumnesConvocatsGestio/{{record.id}}">
                        Gestionar alumnes convocats<br>
                        </a>
                      </li>
                    
                      <li>
                        <a href="/sortides/alumnesFallenGestio/{{record.id}}">
                        Gestionar alumnes que faltaran<br>
                        </a>
                      </li>
                    
                      <li>
                        <a href='javascript:confirmAction("/sortides/esborrarGestio/{{record.id}}"  , "Segur que vols esborrar l'activitat {{record.titol_de_la_sortida}} ?")'>
                        Esborrar<br>
                        </a>
                      </li>
                    
                    </ul>
                  </div>
    """,
    orderable = False, )

    participacio = tables.Column ( orderable = False,)
    n_acompanyants = tables.Column ( orderable = False,)
    
    class Meta:
        model = Sortida
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("estat", "tipus", "titol_de_la_sortida", "ambit", "calendari_desde", "professor_que_proposa", "participacio", "n_acompanyants" )
        fields = sequence
        template = 'bootable2.html'         