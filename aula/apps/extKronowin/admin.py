# This Python file uses the following encoding: utf-8

from django.contrib import admin

from aula.apps.extKronowin.models import Franja2Aula, Grup2Aula, ParametreKronowin

admin.site.register(Franja2Aula)
admin.site.register(Grup2Aula)
admin.site.register(ParametreKronowin)
