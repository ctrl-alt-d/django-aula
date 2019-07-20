# This Python file uses the following encoding: utf-8


from time import strptime, strftime
from django import forms
#from django.db import models
from django.forms import fields
from .widgets import JqSplitDateTimeWidget

#exemple: 
#some_date_field = JqSplitDateTimeField(label=u'Data regeneració',widget=JqSplitDateTimeWidget())
#from utils.fields import  JqSplitDateTimeField
#from utils.widgets import JqSplitDateTimeWidget
class JqSplitDateTimeField(fields.MultiValueField):
    widget = JqSplitDateTimeWidget

    def __init__(self, *args, **kwargs):
        """
        Have to pass a list of field types to the constructor, else we
        won't get any data to our compress method.
        """
        all_fields = (
            fields.CharField(max_length=10),
            fields.CharField(max_length=5, widget=forms.TextInput(attrs={'size':'5'}))
            )
        super(JqSplitDateTimeField, self).__init__(all_fields, *args, **kwargs)

    def compress(self, data_list):
        """
        Takes the values from the MultiWidget and passes them as a
        list to this function. This function needs to compress the
        list into a single object to save.
        """
        if data_list:
            if not (data_list[0] and data_list[1] ):
                raise forms.ValidationError("Data no informada.")
            input_time = strptime(data_list[1], "%H:%M")
            datetime_string = "%s %s" % (data_list[0], strftime('%H:%M', input_time))
            return datetime_string
        return None
