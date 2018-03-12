# This Python file uses the following encoding: utf-8
from aula.apps.sortides.models import Sortida
from django.apps import apps
from datetime import  timedelta

def sincronitza():

    sortides_a_sincronitzar = Sortida.objects.filter( estat_sincronitzacio = Sortida.NO_SINCRONITZADA )
    for instance in list( sortides_a_sincronitzar ):
        
        #marco en sincronitzacio
        instance.estat_sincronitzacio = Sortida.SINCRONITZANT_SE
        instance.save()
        
        #a la llista 'alumnesQueNoVenen' no poden haver altres alumnes dels que apareixen a 'alumnesQueVenen'
        alumnesQueVenen = set( [i.pk for i in instance.alumnes_convocats.all() ] )
        alumnesQueNoVenen = set( [i.pk for i in instance.alumnes_que_no_vindran.all() ] )
        alumnesJustificats = set( [i.pk for i in instance.alumnes_justificacio.all() ] )
        alumnes_fora_aula = ( ( alumnesQueVenen  - alumnesQueNoVenen ) | alumnesJustificats )  or []

        #es fa save controlAssistència per marcar com a no ha de ser present
        NoHaDeSerALAula = apps.get_model('presencia','NoHaDeSerALAula')
        NoHaDeSerALAula.objects.filter( sortida = instance  ).delete()

        ControlAssistencia = apps.get_model(  'presencia.ControlAssistencia' )
        dia_iterador = instance.data_inici
        totes_les_franges = list( apps.get_model(  'horaris.FranjaHoraria' ).objects.all() )
        un_dia = timedelta(days=1)
        while ( bool( dia_iterador ) and 
                dia_iterador <= instance.data_fi and
                instance.estat in ['R','G']):
            controls = list( ControlAssistencia.objects
                             .filter( alumne__in = alumnes_fora_aula,
                                      impartir__dia_impartir = dia_iterador,
                                      impartir__horari__hora__in = totes_les_franges ) )
            for control in controls:
                control.save()
        
            dia_iterador += un_dia   
            
        #marco sincronitzada
        instance.estat_sincronitzacio = Sortida.YES_SINCRONITZADA
        instance.save()
        
            
            