# This Python file uses the following encoding: utf-8
#http://copiesofcopies.org/webl/2010/04/26/a-better-datetime-widget-for-django/

#from django.template.loader import render_to_string
from django.forms.widgets import Select, MultiWidget, DateInput, TextInput
from time import strftime
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape, escape
from django.forms.util import flatatt
from django.utils.encoding import force_unicode
from itertools import chain

#-----------------------------------------------------------------------------------
# És un select per ser omplert via AJAX. Cal passar-li com a paràmetre l'script que l'omplirà
# el javascript s'invoca des d'altres widgets. Ex:   attrs={'onchange':'get_curs();'}

class SelectAjax( Select ):
    
    def __init__(self, jquery=None, attrs=None, choices=(), buit=None):
        self.jquery = jquery if jquery else u''
        self.buit = buit if buit else False
        
        Select.__init__(self, attrs=attrs, choices=choices)
        
    def render(self, name, value, attrs=None, choices=()):
        script =u'<script>%s</script>'%self.jquery

        output = super(SelectAjax, self).render(name, value=value, attrs=attrs, choices=choices)
        return mark_safe(script) + output

    def render_options(self, choices, selected_choices):
        
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if (not self.buit) or (force_unicode(option_value) in selected_choices):
                if isinstance(option_label, (list, tuple)):
                    output.append(u'<optgroup label="%s">' % escape
                     (force_unicode(option_value)))
                    for option in option_label:
                        output.append(self.render_option(selected_choices, *option))
                    
                    output.append(u'</optgroup>')
                else:
                    output.append(self.render_option(selected_choices, 
                     option_value, option_label))
        
        return u'\n'.join(output)    


#-----------------------------------------------------------------------------------

from django.forms import Widget
class label(Widget):
    def __init__(self, attrs=None, format=None):
        super(label, self).__init__(attrs)
    
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        return u'--------> %s'%value 

#http://trentrichardson.com/examples/timepicker/
class JqSplitDateTimeWidget(MultiWidget):

    def __init__(self, attrs=None, date_format=None, time_format=None):

        attrs= attrs if attrs else {'date_class':'datepicker','time_class':'timepicker'}
        date_class = attrs['date_class']
        time_class = attrs['time_class']
        del attrs['date_class']
        del attrs['time_class']

        time_attrs = attrs.copy()
        time_attrs['class'] = time_class
        time_attrs['size'] = '5' 
        time_attrs['maxlength'] = '5' 
        date_attrs = attrs.copy()
        date_attrs['class'] = date_class
        

        widgets = (DateInput(attrs=date_attrs, format=date_format),
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

#-----------------------------------------------------------------------------------
# Adaptació amb botons tipus bootstrap de la funcionalitat dels radiobuttons (Radio
# (c) Joan Rodriguez

class bootStrapButtonSelect(Widget):
    allow_multiple_selected = False

    def render(self, name, value, attrs=None, choices=()):
        id_ = attrs['id']
        num_id = 0
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = ['<div data-toggle="buttons-radio">']
        options = self.render_buttons(choices, id_, num_id, [value])
        if options:
            output.append(options)
        output.append(u'<input type="hidden" value=""%s />' % flatatt(final_attrs))
        output.append(u'</div>')
        return mark_safe(u'\n'.join(output))

    def render_button(self, selected_choices, id_, num_id, option_value, option_label):
        option_value = force_unicode(option_value)
        if option_value in selected_choices:
            selected_html = u' active'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return u'<button type="button" class="btn btn%s%s" id="%s_%s" id_modif="%s" value="%s">%s</button>' % (
            conditional_escape(force_unicode(option_label)),
            selected_html, id_, num_id, id_,
            escape(option_value),
            conditional_escape(force_unicode(option_label)))

    def render_buttons(self, choices, id_, num_id, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_unicode(v) for v in selected_choices)
        output = []
        for option_value, option_label in chain(self.choices, choices):
          output.append(self.render_button(selected_choices, id_, num_id, option_value, option_label))
          num_id = num_id + 1
        return u'\n'.join(output)
