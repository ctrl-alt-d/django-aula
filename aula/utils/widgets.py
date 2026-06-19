# This Python file uses the following encoding: utf-8
# http://copiesofcopies.org/webl/2010/04/26/a-better-datetime-widget-for-django/

from itertools import chain
from time import strftime

from django import forms
from django.forms import Widget
from django.forms.widgets import (
    DateInput,
    DateTimeInput,
    MultiWidget,
    RadioSelect,
    Select,
    TextInput,
)
from django.utils.encoding import force_str
from django.utils.html import conditional_escape, escape
from django.utils.safestring import mark_safe
from django.conf import settings

# -----------------------------------------------------------------------------------
# És un select per ser omplert via AJAX. Cal passar-li com a paràmetre l'script que l'omplirà
# el javascript s'invoca des d'altres widgets. Ex:   attrs={'onchange':'get_curs();'}


class SelectAjax(Select):
    def __init__(self, jquery=None, attrs=None, choices=(), buit=None):
        self.jquery = jquery if jquery else ""
        self.buit = buit if buit else False

        Select.__init__(self, attrs=attrs, choices=choices)

    def render(self, name, value, attrs=None, renderer=None, choices=()):
        script = "<script>%s</script>" % self.jquery

        output = super(SelectAjax, self).render(
            name, value=value, attrs=attrs
        )  # , choices=choices)
        return mark_safe(script) + output

    def render_options(self, choices, selected_choices):
        selected_choices = set([force_str(v) for v in selected_choices])
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if (not self.buit) or (force_str(option_value) in selected_choices):
                if isinstance(option_label, (list, tuple)):
                    output.append(
                        '<optgroup label="%s">' % escape(force_str(option_value))
                    )
                    for option in option_label:
                        output.append(self.render_option(selected_choices, *option))

                    output.append("</optgroup>")
                else:
                    output.append(
                        self.render_option(selected_choices, option_value, option_label)
                    )

        return "\n".join(output)


# -----------------------------------------------------------------------------------


class label(Widget):
    def __init__(self, attrs=None, format=None):
        super(label, self).__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ""
        return "--------> %s" % value


class empty(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        return mark_safe("")


# http://trentrichardson.com/examples/timepicker/
class JqSplitDateTimeWidget(MultiWidget):
    def __init__(self, attrs=None, date_format=None, time_format=None):
        attrs = (
            attrs if attrs else {"date_class": "datepicker", "time_class": "timepicker"}
        )
        date_class = attrs["date_class"]
        time_class = attrs["time_class"]
        del attrs["date_class"]
        del attrs["time_class"]

        time_attrs = attrs.copy()
        time_attrs["class"] = time_class
        time_attrs["size"] = "5"
        time_attrs["maxlength"] = "5"
        date_attrs = attrs.copy()
        date_attrs["class"] = date_class

        widgets = (
            DateInput(attrs=date_attrs, format=date_format),
            TextInput(attrs=time_attrs),
        )

        super(JqSplitDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            d = strftime("%Y-%m-%d", value.timetuple())
            hour = strftime("%H:%M", value.timetuple())
            return (d, hour)
        else:
            return (None, None)

    def format_output(self, rendered_widgets):
        """
        Given a list of rendered widgets (as strings), it inserts an HTML
        linebreak between them.

        Returns a Unicode string representing the HTML for the whole lot.
        """
        return "Dia: %s Hora: %s" % (rendered_widgets[0], rendered_widgets[1])


# -----------------------------------------------------------------------------------
# Adaptació amb botons tipus bootstrap de la funcionalitat dels radiobuttons (Radio
# (c) Joan Rodriguez


class bootStrapButtonSelect2(RadioSelect):
    def render(self, name, value, attrs=None, renderer=None, choices=()):
        print(self)
        print(name)
        print(value)
        print(attrs)
        print(choices)
        output = ['<div class="btn-group" data-toggle="buttons">']
        output.append(super(bootStrapButtonSelect, self).render(self, name, value))
        output.append("</div>")
        return mark_safe("\n".join(output))


class bootStrapButtonSelect(Widget):
    allow_multiple_selected = False

    def render(self, name, value, attrs=None, renderer=None, choices=()):
        id_ = attrs["id"]
        num_id = 0
        if value is None:
            value = ""
        output = ['<div class="btn-group" data-toggle="buttons">']
        options = self.render_buttons(choices, name, id_, num_id, [value])
        if options:
            output.append(options)
        output.append("</div>")
        return mark_safe("\n".join(output))

    def render_button(
        self, selected_choices, name, id_, num_id, option_value, option_label
    ):
        option_value = force_str(option_value)
        if option_value in selected_choices:
            label_selected_html = " active"
            input_selected_html = " checked"
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            label_selected_html = ""
            input_selected_html = ""
        return """<label class="btn btn-default btn%s%s" id="label_%s_%s">
                   <input type="radio" class="rad rad%s" name="%s" value="%s" id="rad_%s_%s" %s />%s</label>""" % (
            conditional_escape(force_str(option_label)),
            label_selected_html,
            id_,
            num_id,
            conditional_escape(force_str(option_label)),
            name,
            escape(option_value),
            id_,
            num_id,
            input_selected_html,
            conditional_escape(force_str(option_label)),
        )

    def render_buttons(self, choices, name, id_, num_id, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_str(v) for v in selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
            output.append(
                self.render_button(
                    selected_choices, name, id_, num_id, option_value, option_label
                )
            )
            num_id = num_id + 1
        return "\n".join(output)


class DateTimeTextImput(DateTimeInput):
    def render(self, name, value, attrs={}, renderer=None):
        pre_html = """
                         <div class='input-group date' id='datetime_{0}' style="width:300px;" >""".format(
            attrs["id"]
        )
        post_html = """    <span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span>
                           </span>
                         </div>
                      """
        javascript = (
            """<script type="text/javascript">
                            $(function () {
                                $('#datetime_"""
            + attrs["id"]
            + """').datetimepicker({
                                    useCurrent: false,
                                    locale: 'ca',
                                    format: 'DD/MM/YYYY HH:mm'
                                });
                            });
                        </script>"""
        )
        attrs.setdefault("class", "")
        attrs["class"] += " form-control"
        attrs["data-format"] = "dd/MM/yyyy hh:mm"
        self.format = "%d/%m/%Y %H:%M"
        super_html = super(DateTimeTextImput, self).render(name, value, attrs)

        return mark_safe(pre_html + super_html + post_html + javascript)


class DateTextImput(DateInput):
    def render(self, name, value, attrs={}, renderer=None):
        pre_html = """
                         <div class='input-group date' id='datetime_{0}' style="width:300px;" >""".format(
            attrs["id"]
        )
        post_html = """    <span class="input-group-addon"><span class="glyphicon glyphicon-calendar"></span>
                           </span>
                         </div>
                      """
        javascript = (
            """<script type="text/javascript">
                            $(function () {
                                $('#datetime_"""
            + attrs["id"]
            + """').datetimepicker({
                                    useCurrent: false,
                                    locale: 'ca',
                                    format: 'DD/MM/YYYY'
                                });
                            });
                        </script>"""
        )
        attrs.setdefault("class", "")
        attrs["class"] += " form-control"
        attrs["data-format"] = "dd/MM/yyyy"
        super_html = super(DateTextImput, self).render(name, value, attrs)

        return mark_safe(pre_html + super_html + post_html + javascript)


class DataHoresAlumneAjax(DateInput):
    """
    Widget que fa servir 2 datetimepicker, serveix per escollir dues dates amb hora inicial i final
    segons horari de l'alumne.
    id_selhores  select per escollir hora de la data seleccionada
    almnid       id de l'alumne usuari actual
    id_dt_end    id del segon datetimepicker per a la data final. Ha de ser None si el widget és el de
                 la data final.

    """

    def __init__(
        self,
        attrs=None,
        format=None,
        id_selhores="",
        almnid=0,
        id_dt_end="",
        pd=None,
        ud=None,
    ):
        self.id_selhores = id_selhores
        self.almnid = str(almnid)
        self.id_dt_end = id_dt_end
        self.pd = str(pd)
        self.ud = str(ud)
        super().__init__(attrs, format)

    def render(self, name, value, attrs=None, renderer=None):
        pre_html = (
            """
                    <div class='input-group date' id='datetime_"""
            + attrs["id"]
            + """' style="width:300px;">"""
        )
        post_html = """ <span class="input-group-addon">
                            <span class="glyphicon glyphicon-calendar"></span>
                        </span>
                    </div>
                    """
        dt_end = (
            """
                        $('#datetime_id_"""
            + self.id_dt_end
            + """').data("DateTimePicker").minDate(valor);
                        $('#datetime_id_"""
            + self.id_dt_end
            + """').data("DateTimePicker").defaultDate(valor);
                 """
            if bool(self.id_dt_end)
            else ""
        )
        javascript = (
            """
            <script type="text/javascript">
                $(function () {
                    $('#datetime_"""
            + attrs["id"]
            + """').datetimepicker({
                         useCurrent: false,
                         locale: 'ca',
                         daysOfWeekDisabled: [0, 6],
                         minDate: new Date('"""
            + self.pd
            + """'),
                         maxDate: new Date('"""
            + self.ud
            + """'),
                         format: 'DD/MM/YYYY'
                    });
                    $('#datetime_"""
            + attrs["id"]
            + """').on("dp.change",function(e){
                        if (!e.date) return;
                        var alumne=\""""
            + self.almnid
            + """\";
                        var valor = new Date(e.date);
                        var dia = valor.getFullYear()+"-"+(valor.getMonth()+1)+"-"+valor.getDate();
                        """
            + dt_end
            + """
                        $('#datetime_"""
            + attrs["id"]
            + """').data("DateTimePicker").hide();
                        $.ajax({type: "GET",
                              url:"/open/horesAlumneAjax/"+alumne+"/"+dia,
                              success:function( res, status) {
                                    if (status == "success") {
                                        $("select#id_"""
            + self.id_selhores
            + """").html( res );
                                     }
                                },
                              error:function (xhr, ajaxOptions, thrownError){
                                        alert(xhr.status);
                                        alert(thrownError);
                                } 
                              });
                    });
                });
            </script>"""
        )

        attrs.setdefault("class", "")
        attrs["class"] += "form-control"
        attrs["data-format"] = "dd/MM/yyyy"
        super_html = super().render(name, value=value, attrs=attrs, renderer=renderer)

        return mark_safe(pre_html + super_html + post_html + javascript)


class image(TextInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        pre_html = ""
        post_html = (
            """
                       <span style="float:left;">
                           <img src="""
            + '"'
            + value.url
            + '"'
            + """ style="height:60px;">
                       </span>
                    """
            if bool(value)
            else ""
        )

        return mark_safe(pre_html + post_html)


class modalButton(TextInput):
    def __init__(self, attrs=None, bname=None, title=None, info=None):
        self.bname = bname if bool(bname) else ""
        self.title = title if bool(title) else ""
        self.info = info if bool(info) else "Sense dades"
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        html = ""

        if bool(value):
            html = """
            <button type="button" class="btn btn-primary" data-toggle="modal" data-target="#{idfield}">{bname}</button>
            <div class="modal fade" id="{idfield}" tabindex="-1" role="dialog" aria-labelledby="myModalLabel{idfield}" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                                <span aria-hidden="true">&times;</span>
                            </button>
                            <h4 class="modal-title" id="myModalLabel{idfield}">{title}</h4>
                        </div>
                        <div class="modal-body">{info}</div>
            
                        <div class="modal-footer">
                            <button type="button" class="btn btn-primary" data-dismiss="modal">Tancar</button>
                        </div>
                    </div>
                </div>
            </div>
                    """.format(
                idfield=attrs["id"], bname=self.bname, title=self.title, info=self.info
            )

        return mark_safe(html)


class CustomClearableFileInput(forms.ClearableFileInput):
    """
    Usa el template 'widgets/dragdrop_upload.html' (CSS + JS integrats).
    - Zona drag & drop, selecció múltiple incremental, eliminar fitxers
      nous en temps real, llista de fitxers existents amb checkbox esborrat.
    Ús: camps d'adjunts en formularis SessionWizardView.
    max_fitxers límit de fitxers a seleccionar. Per defecte valor 0 il·limitat.
    mida_total_bytes límit en bytes entre tots els fitxers. Per defecte valor 0 il·limitat.
    """

    allow_multiple_selected = True
    template_name = "widgets/dragdrop_upload.html"

    def __init__(self, *args, max_fitxers=0, mida_total_bytes=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.eliminaFitxers = []
        self.max_fitxers = max_fitxers
        self.mida_total_bytes = mida_total_bytes

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["attrs"]["max_fitxers"] = self.max_fitxers
        context["widget"]["attrs"]["mida_total_bytes"] = self.mida_total_bytes
        # Passa la llista de mides dels fitxers existents en bytes
        fitxers = self.attrs.get("files", []) if self.attrs else []
        mides = []
        for f in fitxers:
            try:
                # Accedeix directament al fitxer del sistema de fitxers
                import os

                ruta = os.path.join(settings.PRIVATE_STORAGE_ROOT, str(f))
                mides.append(os.path.getsize(ruta))
            except Exception:
                mides.append(0)
        context["widget"]["attrs"]["mides_existents"] = mides
        return context

    def value_from_datadict(self, data, files, name):
        """
        Retorna la llista completa de fitxers pujats (files.getlist)
        i omple self.eliminaFitxers amb els índexs dels checkboxes marcats.
        """
        # ── Tots els fitxers pujats ───────────────────────────────────
        # `files` pot ser un QueryDict (POST real, té getlist) o un dict
        # normal (quan SessionWizardView reconstrueix el form des de sessió).
        if hasattr(files, "getlist"):
            uploads = files.getlist(name)
        else:
            val = files.get(name)
            if val is None:
                uploads = []
            elif isinstance(val, (list, tuple)):
                uploads = list(val)
            else:
                uploads = [val]

        # Checkboxes d'esborrat numerats: 'fitxers-clear1', 'fitxers-clear2'…
        checkbox_prefix = self.clear_checkbox_name(name)
        prefix_len = len(checkbox_prefix)
        self.eliminaFitxers = []
        for key in data.keys():
            # Accepta 'fitxers-clear1', 'fitxers-clear2'…
            # Descarta 'fitxers-clear' exacte (sense número) per no
            # confondre'l amb el checkbox estàndard de ClearableFileInput
            if key.startswith(checkbox_prefix) and len(key) > prefix_len:
                try:
                    num = int(key[prefix_len:])
                    self.eliminaFitxers.append(num)
                except ValueError:
                    pass
        return uploads


class MultipleFileInput(CustomClearableFileInput):
    """
    Widget d'upload amb drag & drop per a formularis simples
    Ús: camps d'adjunts en formularis normals (no SessionWizardView).
    """

    def value_from_datadict(self, data, files, name):
        # Retorna la llista de fitxers; no hi ha checkboxes d'esborrat
        if hasattr(files, "getlist"):
            return files.getlist(name)
        val = files.get(name)
        if val is None:
            return []
        return list(val) if isinstance(val, (list, tuple)) else [val]


class MultipleFileField(forms.FileField):
    """
    Camp que accepta múltiples fitxers.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            if len(data) == 0:
                # Llista buida: delega al FileField base (gestiona required)
                return single_file_clean(data, initial)
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)
