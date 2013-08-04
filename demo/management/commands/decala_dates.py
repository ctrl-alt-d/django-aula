# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from demo.helpers.carrega import fesCarrega
from datetime import date
from aula.apps.alumnes.models import Curs
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from django.db.models import F
from aula.apps.presencia.models import Impartir


class Command(BaseCommand):
    args = 'None'
    help = 'Decalant dates'
    
    
    def handle(self, *args, **options):
        
        un_curs = Curs.objects.all()[0]
        
        data_inici_curs_is = un_curs.data_inici_curs
        data_inici_curs_should_be = date.today() + relativedelta( months = -1)
        
        dies_a_moure = ((data_inici_curs_should_be-data_inici_curs_is).days / 7 ) * 7

        #mou_cursos
        Curs.objects.update( data_inici_curs = F('data_inici_curs') + timedelta(days=dies_a_moure),
                             data_fi_curs = F('data_fi_curs') + timedelta(days=dies_a_moure), ) 
        
        #mou imparticions
        Impartir.objects.update( dia_impartir = F('dia_impartir') + timedelta(days=dies_a_moure) )
        self.stdout.write(u"Dates decalades correctament. Data anterior:{0}, nova data{1}".format(  data_inici_curs_is.strftime("%d/%m/%Y") , ( data_inici_curs_is  + timedelta(days=dies_a_moure)  ).strftime("%d/%m/%Y") ) )

