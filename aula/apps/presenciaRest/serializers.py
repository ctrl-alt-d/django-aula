from rest_framework import serializers
from aula.apps.presencia.models import Impartir, ControlAssistencia, EstatControlAssistencia
from aula.apps.horaris.models import Horari
from aula.apps.assignatures.models import Assignatura
from .utils import ControlAssistenciaIHoraAnterior

class AssignaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignatura
        fields = ['curs', 'tipus_assignatura', 'codi_assignatura', 'nom_assignatura']

class HorariSerializer(serializers.ModelSerializer):
    assignatura=AssignaturaSerializer(many=False, read_only=True)
    class Meta:
        model = Horari
        fields = ['assignatura', 'professor', 'grup', 
        'dia_de_la_setmana', 'hora', 'nom_aula', 'aula','es_actiu','estat_sincronitzacio']

class ImpartirSerializer(serializers.ModelSerializer):
    horari = HorariSerializer(many=False, read_only=True)
    class Meta:
        model = Impartir
        fields = ['horari' ,'professor_guardia', 'professor_passa_llista', 'dia_impartir', 
        'dia_passa_llista', 'comentariImpartir', 'pot_no_tenir_alumnes', 'reserva']

class ControlAssistenciaIHoraAnteriorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlAssistenciaIHoraAnterior
        fields = ['alumne', 'estat', 'impartir', 'professor','estatHoraAnterior','nomAlumne','cognomsAlumne']