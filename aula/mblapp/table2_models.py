# This Python file uses the following encoding: utf-8
import django_tables2 as tables
from django_tables2.utils import A

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from aula.apps.usuaris.models import QRPortal

class Table2_QRPortal(tables.Table):

    class Meta:
        model = QRPortal
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        sequence = ("moment_expedicio", "moment_captura", "moment_confirmat_pel_tutor" )
        fields = sequence
        template = 'bootable2.html'