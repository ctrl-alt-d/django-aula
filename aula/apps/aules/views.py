# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#workflow
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect

#auth
from django.contrib.auth.decorators import login_required

#models
from aula.apps.aules.models import Aula, ReservaAula

#forms
from aula.apps.aules.forms import disponibilitatAulaForm, triaAulaSelect2Form

#helpers
from aula.utils.decorators import group_required
from aula.utils import tools
from aula.utils.widgets import DateTimeTextImput,DateTextImput
from django.utils.datetime_safe import datetime
from django.forms.models import modelform_factory

@login_required
@group_required(['professors', 'professional'])
def consultaAula(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    formset = []
    if request.method == 'POST':
        formDisponibilitatAula = disponibilitatAulaForm(request.POST)
        formAula = triaAulaSelect2Form(request.POST)

        if formAula.is_valid() and formDisponibilitatAula.is_valid():
            aula = formAula.cleaned_data['aula']
            data = formDisponibilitatAula.cleaned_data['data']
            print aula
            print data
            next_url = r'/aules/reservaAulaHorari/{0}/{1}'
            return HttpResponseRedirect(next_url.format(aula.pk,data))
        else:
            print "aaaa"


        # expulsio = Expulsio()
        # expulsio.credentials = credentials
        # expulsio.professor_recull = User2Professor(user)
        #
        # formAlumne = triaAlumneSelect2Form(request.POST)
        # formExpulsio = posaExpulsioForm(data=request.POST, instance=expulsio)
        #
        # if formAlumne.is_valid():
        #     expulsio.alumne = formAlumne.cleaned_data['alumne']
        #     if formExpulsio.is_valid():
        #         expulsio.save()
        #
        #         url = '/incidencies/posaExpulsioW2/{u}'.format(u=expulsio.pk)
        #
        #         return HttpResponseRedirect(url)
        #
        # else:
        #     formset.append(formAlumne)
        #     formset.append(formExpulsio)

    else:

        formDisponibilitatAula = disponibilitatAulaForm()
        formAula = triaAulaSelect2Form
        formset.append(formAula)
        formset.append(formDisponibilitatAula)


    return render(
        request,
        'formset.html',
        {'formset': formset,
         'head': u'Consultar disponibilitat aula',
         },
    )