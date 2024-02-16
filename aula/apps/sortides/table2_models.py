# -*- encoding: utf-8 -*-
import django_tables2 as tables
from django_tables2.utils import A

from django.utils.safestring import mark_safe
from django.urls import reverse

from aula.apps.sortides.models import Sortida

class Table2_Sortides(tables.Table):
    
    #titol_de_la_sortida = tables.LinkColumn('sortides__sortides__editGestio_by_pk', kwargs={'pk': A('pk'),})
    participacio = tables.Column ( orderable = False,)
    accions = tables.TemplateColumn( template_code="x", orderable = False, )

    participacio = tables.Column ( orderable = False,)
    n_acompanyants = tables.TemplateColumn ( verbose_name=u"Acompanyants", template_code="{{record.n_acompanyants}}", orderable = False,)
    
    professor_que_proposa = tables.Column ( order_by=("professor_que_proposa.last_name", "professor_que_proposa.first_name") )
    
    #migracio bootstrap 3.1.1: http://stackoverflow.com/questions/18892351/bootstrap-dropdown-bubble-align-right-not-push-right
    
    def __init__(self, data, origen, *args, **kwargs):
        accions_html=""
        if origen=="Gestio":
            accions_html= u"""
                    <div class="btn-group btn-group-xs">
                        <a class="btn dropdown-toggle btn-primary btn-xs" data-toggle="dropdown" href="#">
                          Accions
                          <span class="caret"></span>
                        </a>
                        <ul class="dropdown-menu pull-right dropdown-menu-right">
                        
                          <li>
                            <a href="/sortides/sortidaEditGestio/{{record.id}}/{{record.tipus}}">
                            Modificar dades<br>
                            </a>
                          </li>
                        
                          <li>
                            <a href="/sortides/alumnesConvocatsGestio/{{record.id}}">
                            Alumnat seleccionat<br>
                            </a>
                          </li>
                          {% if record.tipus != "P" %}
                              <li>
                                <a href="/sortides/alumnesFallenGestio/{{record.id}}">
                                Alumnes no assistents a l'activitat<br>
                                </a>
                              </li>
                              <li>
                                <a href="/sortides/alumnesJustificatsGestio/{{record.id}}">
                                Alumnes no assistents a l'activitat ni al centre<br>
                                </a>
                              </li>
                              <li>
                                <a href="/sortides/professorsAcompanyantsGestio/{{record.id}}">
                                Professors acompanyants<br>
                                </a>
                              </li>
                          {% endif %}   
    
                          {% if record.tipus_de_pagament == "ON" %}
                            <li>
                                <a href="/sortides/detallPagament/{{record.id}}">
                                Dades pagament<br>
                                </a>
                            </li>
                          {% endif %}   
                                          
                          <li>
                            <a href="/sortides/sortidaExcel/{{record.id}}">
                            Descarregar dades en Excel<br>
                            </a>
                          </li>
                          {% if record.tipus != "P" %}
                              <li>
                                <a href="/sortides/imprimir/{{record.id}}/4">
                                Imprimir fulls autorització i pagament<br>
                                </a>
                              </li>
                          {% endif %}   
                          <li>
                            <a href="/sortides/imprimir/{{record.id}}/5">
                            Imprimir fulls de pagament<br>
                            </a>
                          </li>
                                                                                                            
                          <li>
                            <a href='javascript:confirmAction("/sortides/esborrarGestio/{{record.id}}"  , " {{ "Segur que vols esborrar l'activitat"|escapejs}} {{record.titol}} ?")'>
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
                    <ul class="dropdown-menu pull-right dropdown-menu-right">
                    
                      <li>
                        <a href="/sortides/sortidaEdit/{{record.id}}/{{record.tipus}}">
                        Modificar dades<br>
                        </a>
                      </li>
                    
                      <li>
                        <a href="/sortides/alumnesConvocats/{{record.id}}">
                        Alumnes convocats<br>
                        </a>
                      </li>
                      {% if record.tipus != "P" %}
                          <li>
                            <a href="/sortides/alumnesFallen/{{record.id}}">
                            Alumnes no assistents a l'activitat<br>
                            </a>
                          </li>
    
                          <li>
                            <a href="/sortides/alumnesJustificats/{{record.id}}">
                            Alumnes no assistents a l'activitat ni al centre<br>
                            </a>
                          </li>
                                                  
                          <li>
                            <a href="/sortides/professorsAcompanyants/{{record.id}}">
                            Professors acompanyants<br>
                            </a>
                          </li>  
                      {% endif %}   
   
                      {% if record.tipus_de_pagament == "ON" %}
                        <li>
                            <a href="/sortides/detallPagament/{{record.id}}">
                            Dades pagament<br>
                            </a>
                        </li>
                      {% endif %}    
                        
                      <li>
                        <a href="/sortides/sortidaExcel/{{record.id}}">
                        Descarregar dades en Excel<br>
                        </a>
                      </li>            
                      
                          {% if record.tipus != "P" %}
                              <li>
                                <a href="/sortides/imprimir/{{record.id}}/4">
                                Imprimir fulls autorització i pagament<br>
                                </a>
                              </li>
                          {% endif %}  
                          
                          <li>
                            <a href="/sortides/imprimir/{{record.id}}/5">
                            Imprimir fulls de pagament<br>
                            </a>
                          </li>
                                                              
                      <li>
                        <a href='javascript:confirmAction("/sortides/esborrar/{{record.id}}"  , "{{ "Segur que vols esborrar l'activitat/pagament"|escapejs}} {{record.titol|escapejs }} ?")'>
                        Esborrar<br>
                        </a>
                      </li>

                      <li>
                        <a href="/sortides/sortidaClonar/{{record.id}}/{{record.tipus}}">
                        Clonar<br>
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
                        <ul class="dropdown-menu pull-right dropdown-menu-right">
                        
                          <li>
                            <a href="/sortides/sortidaEditAll/{{record.id}}/{{record.tipus}}">
                            Modificar dades<br>
                            </a>
                          </li>
                        
                          <li>
                            <a href="/sortides/alumnesConvocatsAll/{{record.id}}">
                            Alumnes convocats<br>
                            </a>
                          </li>
                          {% if record.tipus != "P" %}
                              <li>
                                <a href="/sortides/alumnesFallenAll/{{record.id}}">
                                Alumnes no assistents a l'activitat<br>
                                </a>
                              </li>
    
                              <li>
                                <a href="/sortides/alumnesJustificatsAll/{{record.id}}">
                                Alumnes no assistents a l'activitat ni al centre<br>
                                </a>
                              </li>
    
                              <li>
                                <a href="/sortides/professorsAcompanyantsAll/{{record.id}}">
                                Professors acompanyants<br>
                                </a>
                              </li>
                          {% endif %}    
                          {% if record.tipus_de_pagament == "ON" %}
                            <li>
                                <a href="/sortides/detallPagament/{{record.id}}">
                                    Dades pagament<br>
                                </a>
                            </li>
                           {% endif %}   
                                          
                          <li>
                            <a href="/sortides/sortidaExcel/{{record.id}}">
                            Descarregar dades en Excel<br>
                            </a>
                          </li>
                          
            
                          {% if record.tipus != "P" %}
                              <li>
                                <a href="/sortides/imprimir/{{record.id}}/4">
                                Imprimir fulls autorització i pagament<br>
                                </a>
                              </li>
                          {% endif %}  
                          
                          <li>
                            <a href="/sortides/imprimir/{{record.id}}/5">
                            Imprimir fulls de pagament<br>
                            </a>
                          </li>
                                              
                          <li>
                            <a href='javascript:confirmAction("/sortides/esborrarAll/{{record.id}}"  , " {{ "Segur que vols esborrar l'activitat"|escapejs}} {{record.titol}} ?")'>
                            Esborrar<br>
                            </a>
                          </li>
                        
                        </ul>
                      </div>
            """
        elif origen=="Tutoria":
            accions_html= u"""
                <div class="btn-group btn-group-xs">
                    <a class="btn dropdown-toggle btn-primary btn-xs" data-toggle="dropdown" href="#">
                      Accions
                      <span class="caret"></span>
                    </a>
                    <ul class="dropdown-menu pull-right dropdown-menu-right">
                      {% if record.tipus != "P" %}                
                          <li>
                            <a href="/tutoria/justificarSortidaAlumne/{{record.id}}">
                            Alumnes no assistents a l'activitat ni al centre<br>
                            </a>
                          </li>                    
                      {% endif %}  
                    </ul>
                  </div>
            """

        super(Table2_Sortides, self).__init__(data, *args, **kwargs)
        self.columns['accions'].column.template_code = accions_html
        #if origen == "Gestio":
        self.columns['n_acompanyants'].column.template_code = "{{record.nom_acompanyants}}"
        if origen=="Consergeria":
            self.exclude=("accions", "estat", "professor_que_proposa")
        self.base_columns['subtipus'].verbose_name = "Tipus"
    class Meta:
        model = Sortida
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("estat", "subtipus", "titol", "ciutat", "ambit", "calendari_desde", "calendari_finsa", "professor_que_proposa", "participacio", "n_acompanyants", "termini_pagament" )
        fields = sequence
        template = 'bootable2.html'      
        
  