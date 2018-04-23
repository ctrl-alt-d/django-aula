# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings

from django.shortcuts import  get_object_or_404
from django.http import  HttpResponse, HttpResponseForbidden

#auth
from django.contrib.auth.decorators import login_required

#models
from aula.apps.aules.models import Aula, ReservaAula

#helpers
from aula.apps.usuaris.models import User2Professor
from aula.utils.decorators import group_required
from aula.utils import tools
from django.utils.datetime_safe import datetime
import datetime as diahora

#@login_required
#@group_required(['professors', 'professional','consergeria'])
def getStatus( request ):
    #(user, l4) = tools.getImpersonateUser(request)
    #professor = User2Professor( user )

    nom_aula = request.GET.get('aula', None)
    key = request.GET.get('key',None)
    if key!=settings.CUSTOM_RESERVES_API_KEY:
        return HttpResponseForbidden()
    if key=='dfsjkjf34q9r4398reorti':
        content = 'Fora de Servei'
        return HttpResponse(content, content_type='text/plain; charset=utf-8')

    aula = get_object_or_404(Aula, nom_aula = nom_aula)
    ara = datetime.now().time()
    reservasDAulaAvui = ReservaAula.objects.filter(aula = aula,
                                                   dia_reserva = datetime.today(),
                                                   hora_fi__gt = ara
                                                   ) if aula else None

    content =''
    dateTimeAra = diahora.datetime.combine(diahora.date.today(), ara)
    if not reservasDAulaAvui: content = 'Aula lliure tot el dia'
    for reserva in reservasDAulaAvui:
            if reserva.hora_inici < ara:
                dateTimeFi = diahora.datetime.combine(diahora.date.today(), reserva.hora_fi)
                dif = dateTimeAra - dateTimeFi
                difInMinuts = int(round(dif.total_seconds() / 60))
                content = 'now: \n{0} minuts'.format(difInMinuts)
            else:
                dateTimeInici =  diahora.datetime.combine(diahora.date.today(), reserva.hora_inici)
                dif = dateTimeInici - dateTimeAra
                difInMinuts = int(round(dif.total_seconds()/60))
                content = content + "\nnext: \n+{0} minuts".format(difInMinuts)
            motiu = reserva.get_assignatures if reserva.associada_a_impartir else reserva.motiu
            grup = reserva.get_grups if reserva.associada_a_impartir else '---'

            content = content+u"\n{0}\n{1} {2}\n{3}\n{4}".format(reserva.usuari,
                                                            reserva.usuari.first_name,
                                                            reserva.usuari.last_name,
                                                            motiu,
                                                            grup)

    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    return response

