# -*- encoding: utf-8 -*-
import django_tables2 as tables
from django_tables2.utils import A

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from aula.apps.sortides.models import Sortida

class Table2_Sortides(tables.Table):
    
    #titol_de_la_sortida = tables.LinkColumn('sortides__sortides__editGestio_by_pk', kwargs={'pk': A('pk'),})
    participacio = tables.Column ( orderable = False,)
    accions = tables.TemplateColumn( template_code="x", orderable = False, )

    participacio = tables.Column ( orderable = False,)
    n_acompanyants = tables.TemplateColumn ( template_code="{{record.n_acompanyants}}", orderable = False,)
    
    professor_que_proposa = tables.Column ( order_by=("professor_que_proposa__last_name", "professor_que_proposa__first_name") )
    
    def __init__(self, data, origen, *args, **kwargs):
        accions_html=""
        if origen=="Gestio":
            accions_html= u"""
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
                            <a href="/sortides/professorsAcompanyantsGestio/{{record.id}}">
                            Professors acompanyants<br>
                            </a>
                          </li>
                                                  
                          <li>
                            <a href='javascript:confirmAction("/sortides/esborrarGestio/{{record.id}}"  , " {{ "Segur que vols esborrar l'activitat"|escapejs}} {{record.titol_de_la_sortida}} ?")'>
                            Esborrar<br>
                            </a>
                          </li>
                        
                        </ul>
                      </div>
            """
        elif origen=="Meves":
            accions_html= u"""
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
                        <a href='javascript:confirmAction("/sortides/esborrar/{{record.id}}"  , "{{ "Segur que vols esborrar l'activitat"|escapejs}} {{record.titol_de_la_sortida|escapejs }} ?")'>
                        Esborrar<br>
                        </a>
                      </li>
                    
                    </ul>
                  </div>
            """        
        elif origen=="All":
            accions_html= u"""
                    <div class="btn-group btn-group-xs">
                        <a class="btn dropdown-toggle btn-primary btn-xs" data-toggle="dropdown" href="#">
                          Accions
                          <span class="caret"></span>
                        </a>
                        <ul class="dropdown-menu">
                        
                          <li>
                            <a href="/sortides/sortidaEditAll/{{record.id}}">
                            Modificar dades<br>
                            </a>
                          </li>
                        
                          <li>
                            <a href="/sortides/alumnesConvocatsAll/{{record.id}}">
                            Gestionar alumnes convocats<br>
                            </a>
                          </li>
                        
                          <li>
                            <a href="/sortides/alumnesFallenAll/{{record.id}}">
                            Gestionar alumnes que faltaran<br>
                            </a>
                          </li>

                          <li>
                            <a href="/sortides/professorsAcompanyantsAll/{{record.id}}">
                            Professors acompanyants<br>
                            </a>
                          </li>
                                              
                          <li>
                            <a href='javascript:confirmAction("/sortides/esborrarAll/{{record.id}}"  , " {{ "Segur que vols esborrar l'activitat"|escapejs}} {{record.titol_de_la_sortida}} ?")'>
                            Esborrar<br>
                            </a>
                          </li>
                        
                        </ul>
                      </div>
            """

        super(Table2_Sortides, self).__init__(data, *args, **kwargs)        
        self.columns['accions'].column.template_code = accions_html
        if origen == "Gestio":
            self.columns['n_acompanyants'].column.template_code = "{{record.nom_acompanyants}}"
    
    class Meta:
        model = Sortida
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("estat", "tipus", "titol_de_la_sortida", "ambit", "calendari_desde", "professor_que_proposa", "participacio", "n_acompanyants" )
        fields = sequence
        template = 'bootable2.html'      
        
  