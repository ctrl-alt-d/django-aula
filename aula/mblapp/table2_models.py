# This Python file uses the following encoding: utf-8
import django_tables2 as tables

from aula.apps.alumnes.models import Alumne


class Table2_QRPortalAlumne(tables.Table):
    data_expedicio = tables.TemplateColumn(
        template_code=u"""{{ record.moment_expedicio }}""",
    )
    data_captura = tables.TemplateColumn(
        template_code=u"""{%if record.moment_captura%} {{ record.moment_captura }} {%else%} ----- {%endif%}""",
    )
    actiu = tables.TemplateColumn(
        template_code=u"""{%if record.es_el_token_actiu%} Sí {%else%} No {%endif%}""",
    )
    data_confirmacio_pel_tutor = tables.TemplateColumn(
        template_code=u"""{%if record.moment_confirmat_pel_tutor%} {{record.moment_confirmat_pel_tutor}} {%else%} ----- {%endif%}""",    )

    accions = tables.TemplateColumn(template_code=u"""
                    <div class="btn-group btn-group-xs">
                        <a class="btn dropdown-toggle btn-primary btn-xs" data-toggle="dropdown" href="#">
                          Accions
                          <span class="caret"></span>
                        </a>
                        <ul class="dropdown-menu pull-right dropdown-menu-right">
                        {%if record.moment_captura and not record.es_el_token_actiu%}
                          <li>
                            <a href="/usuaris/activaUsuariQR/{{record.pk}}">
                            Activar<br>
                            </a>
                          </li>
                        {%endif%}

                        {%if record.es_el_token_actiu%}
                          <li>
                            <a href="/usuaris/desactivaUsuariQR/{{record.pk}}">
                             Desactivar<br>
                            </a>
                          </li>
                        {%endif%}


                        <li>
                            <a href='javascript:confirmAction("/usuaris/eliminaUsuariQR/{{record.pk}}" , " {{ "Segur que vols eliminar el QR generat per a l'alumne/a"|escapejs}} {{record.alumne_referenciat}}{{", el dia"|escapejs}} {{record.moment_expedicio}} ?")'>
                            Eliminar<br>
                            </a>
                        </li>
                        </ul>
                      </div>
            """
                                    , orderable=True, )
    class Meta:
        model = Alumne
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("data_expedicio", "data_captura", "data_confirmacio_pel_tutor", "actiu", )
        fields = sequence
        order_by = ("-data_expedicio")
        template = 'bootable2.html'