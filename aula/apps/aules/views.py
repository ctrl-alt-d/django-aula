# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#workflow
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
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

    franges_del_dia = ( FranjaHoraria
                       .objects
                       .filter( horari__impartir__dia_impartir = data )
                       .order_by('hora_inici')
                      )
    primera_franja = franges_del_dia.first()
    darrera_franja = franges_del_dia.last()

    franges_reservables = ( FranjaHoraria
                            .objects
                            .filter(hora_inici__gte = primera_franja.hora_inici)
                            .filter(hora_fi__lte = darrera_franja.hora_fi)
                            ) if primera_franja and darrera_franja else []


    reserves_dun_dia_un_aula = ( ReservaAula
                                .objects
                                .filter(aula=aula)
                                .filter(dia_reserva=data) )

    reserves = []
    for franja in franges_reservables:
        reserva = reserves_dun_dia_un_aula.filter(hora=franja).order_by().first()
        nova_franja = {}
        nova_franja['franja'] = franja
        nova_franja['reserva'] = reserva
        nova_franja['assignatura'] = u", ".join( reserva.impartir_set.values_list( 'horari__assignatura__nom_assignatura', flat=True ).distinct() ) if reserva else u""
        nova_franja['grup'] = u", ".join( reserva.impartir_set.values_list( 'horari__grup__descripcio_grup', flat=True ).distinct() )  if reserva else u""
        nova_franja['professor'] = u", ".join([reserva.usuari.first_name + ' ' + reserva.usuari.last_name]) if reserva else u""
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
         'usuari': user.first_name + ' ' + user.last_name,
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
        missatge = u"Ho sentim, s'ha detectat un problema amb la reserva"
        if form.is_valid():
            try:
                reserva=form.save()
                missatge = u"Reserva realitzada correctament"
                messages.info(request, missatge)
                return HttpResponseRedirect(
                    r'/aules/reservaAulaHorari/{0}/{1}/{2}/{3}/'.format(year, month, day, reserva.aula.pk))
            except ValidationError, e:
                for _, v in e.message_dict.items():
                    form._errors.setdefault(NON_FIELD_ERRORS, []).extend(v)

        messages.info(request, missatge)
    else:
        form = reservaAulaForm(instance=novaReserva)

    form.fields['aula'].widget.attrs['readonly'] = True
    form.fields['hora'].widget.attrs['readonly'] = True
    form.fields['hora_inici'].widget = forms.HiddenInput()
    form.fields['hora_fi'].widget = forms.HiddenInput()
    #form.fields['hora_inici'].widget.attrs['readonly'] = True
    #form.fields['hora_fi'].widget.attrs['readonly'] = True
    form.fields['dia_reserva'].widget.attrs['readonly'] = True
    form.fields['usuari'].widget = forms.HiddenInput()
    form.fields['usuari'].widget.attrs['readonly'] = True

    return render(
            request,
            'form.html',
            {'form': form,
             'head': u'Reservar aula',
             },
    )


@login_required
@group_required(['professors', 'professional'])
def eliminarReservaAula (request, pk, pk_aula, year, month, day):

    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials
    reserva = get_object_or_404(ReservaAula, pk=pk)

    missatge = u"Reserva anul·lada correctament"
    try:
            reserva.delete()
            messages.info(request, missatge)
            return HttpResponseRedirect(
                r'/aules/reservaAulaHorari/{0}/{1}/{2}/{3}/'.format(year, month, day, pk_aula))
    except (Exception, reserva) :
            missatge = u"Ho sentim, no s'ha pogut anul·lar la reserva: " + reserva
            messages.info(request, missatge)


