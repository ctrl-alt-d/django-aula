# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings

from django.shortcuts import  get_object_or_404
from django.http import  HttpResponse, HttpResponseForbidden

#auth
from django.contrib.auth.decorators import login_required

#models
from aula.apps.aules.models import Aula, ReservaAula
from aula.apps.horaris.models import FranjaHoraria

#helpers
from aula.apps.usuaris.models import User2Professor
from aula.utils.decorators import group_required
from aula.utils import tools
from datetime import datetime, date

#@login_required
#@group_required(['professors', 'professional','consergeria'])
def getStatus( request ):
    #(user, l4) = tools.getImpersonateUser(request)
    #professor = User2Professor( user )

    nom_aula = request.GET.get('aula', None)
    key = request.GET.get('key',None)
    outputformat = request.GET.get('outputformat',None)
    
    if key!=settings.CUSTOM_RESERVES_API_KEY:
        return HttpResponseForbidden()
    if key=='_default_api_aules_password_':
        content = 'Fora de Servei'
        return HttpResponse(content, content_type='text/plain; charset=utf-8')

    aula = Aula.objects.filter( nom_aula = nom_aula).first()
    if not aula:
        content = 'Aula no existeix'
        return HttpResponse(content, content_type='text/plain; charset=utf-8')   

    ara = datetime.now().time()
    reservasDAulaAvui = ReservaAula.objects.filter(aula = aula,
                                                   dia_reserva = datetime.today(),
                                                   hora_fi__gt = ara
                                                   ) 

    content =''
    dateTimeAra = datetime.combine(date.today(), ara)

    if outputformat == "2liniesNow":
        franjaActual = ( FranjaHoraria
                        .objects
                        .filter(  hora_inici__lte = ara )
                        .filter(  hora_fi__gte = ara )
                        .first()
                        )
        reserves_ara = reservasDAulaAvui.filter( hora = franjaActual )
        profes_ara = u",".join([ r.usuari.username for r in reserves_ara ]) or u"lliure"

        content = u"""{franja}\n{profes}\n""".format(franja = franjaActual, 
                                                   profes =  profes_ara,)
        return HttpResponse(content, content_type='text/plain; charset=utf-8')  

    if outputformat == "2liniesNext":
        seguent_franja = ( FranjaHoraria
                        .objects
                        .filter(  hora_inici__gte = ara )
                        .order_by(  "hora_inici" )
                        .first()
                        )
        reserves_despres = reservasDAulaAvui.filter( hora = seguent_franja )
        profes_despres = u",".join([ r.usuari.username for r in reserves_despres ]) or u"lliure"

        content = u"""{franja}\n{profes}\n""".format(franja = seguent_franja, 
                                                   profes =  profes_despres,)
        return HttpResponse(content, content_type='text/plain; charset=utf-8')     

    if outputformat == "2linies":
        franjaActual = ( FranjaHoraria
                        .objects
                        .filter(  hora_inici__lte = ara )
                        .filter(  hora_fi__gte = ara )
                        .first()
                        )
        reserves_ara = reservasDAulaAvui.filter( hora = franjaActual )
        profes_ara = u",".join([ r.usuari.username for r in reserves_ara ]) or u"lliure"

        seguent_franja = ( FranjaHoraria
                        .objects
                        .filter(  hora_inici__gte = ara )
                        .order_by(  "hora_inici" )
                        .first()
                        )
        reserves_despres = reservasDAulaAvui.filter( hora = seguent_franja )
        profes_despres = u",".join([ r.usuari.username for r in reserves_despres ]) or u"lliure"

        content = u"""{franja1} {profes1}\n{franja2} {profes2}\n""".format(
                              franja1 = franjaActual, profes1 =  profes_ara,
                              franja2 = seguent_franja, profes2 =  profes_despres,)
        return HttpResponse(content, content_type='text/plain; charset=utf-8')     

    if not reservasDAulaAvui: 
        content = 'Aula lliure tot el dia'
        return HttpResponse(content, content_type='text/plain; charset=utf-8')          

    for reserva in reservasDAulaAvui:
            if reserva.hora_inici < ara:
                dateTimeFi = datetime.combine(date.today(), reserva.hora_fi)
                dif = dateTimeAra - dateTimeFi
                difInMinuts = int(round(dif.total_seconds() / 60))
                content = 'now: \n{0} minuts'.format(difInMinuts)
            else:
                dateTimeInici =  datetime.combine(date.today(), reserva.hora_inici)
                dif = dateTimeInici - dateTimeAra
                difInMinuts = int(round(dif.total_seconds()/60))
                content = content + "\nnext: \n+{0} minuts".format(difInMinuts)
            motiu = reserva.get_assignatures if reserva.associada_a_impartir else reserva.motiu
            grup = reserva.get_grups if reserva.associada_a_impartir else '---'

            content = content+u"\n{0}\n{1} {2}\n{3}\n{4}\n".format(reserva.usuari,
                                                            reserva.usuari.first_name,
                                                            reserva.usuari.last_name,
                                                            motiu,
                                                            grup)

    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    return response

