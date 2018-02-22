# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#workflow
from django.shortcuts import render, get_object_or_404
from django import forms
from django.http import HttpResponseRedirect

#auth
from django.contrib.auth.decorators import login_required

#tables
from django_tables2 import RequestConfig
from aula.apps.aules.tables2_models import HorariAulaTable

#models

from aula.apps.aules.models import Aula, ReservaAula
from aula.apps.horaris.models import FranjaHoraria, Horari

#forms
from aula.apps.aules.forms import disponibilitatAulaForm, triaAulaSelect2Form, reservaAulaForm

#helpers
from aula.utils.decorators import group_required
from aula.utils import tools
from django.contrib import messages
from django.utils.datetime_safe import datetime


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
            year = data.year
            month = data.month
            date = data.day
            next_url = r'/aules/reservaAulaHorari/{0}/{1}/{2}/{3}'
            return HttpResponseRedirect(next_url.format(year, month, date, aula.pk))


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


@login_required
@group_required(['professors', 'professional'])
def detallAulaReserves (request, year, month, day, pk):

    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    aula = get_object_or_404(Aula, pk=pk)

    import datetime as t
    if not ( year and month and day):
        today = t.date.today()
        year = today.year
        month = today.month
        day = today.day
    else:
        year= int( year)
        month = int( month )
        day = int( day)
    data = t.date(year, month, day)

    reserves = []

    reserves_dun_dia = ReservaAula.objects.filter(dia_reserva=data)
    franjes_dun_dia = [reserva.hora for reserva in reserves_dun_dia]
    franjes_uniques_dun_dia = []
    franja_maxima_dun_dia = franjes_dun_dia[0] if franjes_dun_dia else None
    for franja in franjes_dun_dia:
        if franja not in franjes_uniques_dun_dia:
            franjes_uniques_dun_dia.append(franja)
        if franja.hora_fi > franja_maxima_dun_dia.hora_fi:
            franja_maxima_dun_dia = franja
    reserves_dun_dia_un_aula = reserves_dun_dia.filter(aula__nom_aula=aula.nom_aula)

    if franja_maxima_dun_dia:
        for franja in FranjaHoraria.objects.all():
            if franja.hora_fi <= franja_maxima_dun_dia.hora_fi:
                nova_franja = {}
                nova_franja['franja'] = franja
                hora_reservada = reserves_dun_dia_un_aula.filter(hora=franja)
                nova_franja['reserva'] = hora_reservada[0] if hora_reservada else None
                horari = Horari.objects.filter(aula__nom_aula = aula.nom_aula, hora = franja, dia_de_la_setmana = data.weekday()+1 )
                assignatura = horari[0].assignatura if horari else ""
                grup = horari[0].grup if horari else ""
                reservaaula = ReservaAula.objects.filter (aula__nom_aula = aula.nom_aula, hora=franja, dia_reserva=data)
                professor = horari[0].professor if horari else reservaaula[0].usuari.first_name+" " +reservaaula[0].usuari.last_name if reservaaula else ""
                nova_franja['assignatura'] = assignatura
                nova_franja['grup'] = grup
                nova_franja['professor'] = professor
                reserves.append(nova_franja)

    table = HorariAulaTable(reserves)
    table.order_by = 'franja'
    RequestConfig(request).configure(table)

    return render(
        request,
        'mostraInfoReservaAula.html',
        {'table': table,
         'aula': aula,
         'dia': data,
         },
    )




@login_required
@group_required(['professors', 'professional'])
def tramitarReservaAula (request, pk, pk_franja , year, month, day):

    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    aula = get_object_or_404(Aula, pk=pk)
    franja = get_object_or_404(FranjaHoraria,pk=pk_franja)

    import datetime as t
    if not (year and month and day):
        today = t.date.today()
        year = today.year
        month = today.month
        day = today.day
    else:
        year = int(year)
        month = int(month)
        day = int(day)
    data = t.date(year, month, day)


    novaReserva = ReservaAula(aula=aula,
                              hora=franja,
                              hora_inici=franja.hora_inici,
                              hora_fi=franja.hora_fi,
                              dia_reserva=data,
                              usuari=user)
    if request.method=='POST':
        form = reservaAulaForm(request.POST, instance=novaReserva)
        if form.is_valid():
            form.save()
            missatge = u"Reserva realitzada correctament"
            return HttpResponseRedirect(r'/aules/reservaAulaHorari/{0}/{1}/{2}/{3}/'.format(year,month,day,pk))
        else:
            missatge = u"Ho sentim, s'ha detectat un problema amb la reserva"
        messages.info(request, missatge)
    else:
        form = reservaAulaForm(instance=novaReserva)


    form.fields['aula'].widget.attrs['readonly'] = True
    form.fields['hora'].widget.attrs['readonly'] = True
    form.fields['hora_inici'].widget.attrs['readonly'] = True
    form.fields['hora_fi'].widget.attrs['readonly'] = True
    form.fields['dia_reserva'].widget.attrs['readonly'] = True
    form.fields['usuari'].widget.attrs['readonly'] = True



    return render(
            request,
            'form.html',
            {'form': form,
             'head': u'Reservar aula',
             },
    )
