from rest_framework import serializers
from aula.apps.presencia.models import Impartir, ControlAssistencia, EstatControlAssistencia
from aula.apps.horaris.models import Horari, FranjaHoraria
from aula.apps.assignatures.models import Assignatura
from aula.apps.usuaris.models import Professor
from .utils import ControlAssistenciaIHoraAnterior

class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['id','username','first_name','last_name','groups']

class EstatControlAssistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstatControlAssistencia
        fields = '__all__'

class FranjaHorariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FranjaHoraria
        fields = '__all__'

class AssignaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignatura
        fields = ['id', 'curs', 'tipus_assignatura', 'codi_assignatura', 'nom_assignatura']

class FranjaHorariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FranjaHoraria
        fields = '__all__'

class HorariSerializer(serializers.ModelSerializer):
    assignatura=AssignaturaSerializer(many=False, read_only=True)
    hora=FranjaHorariaSerializer(many=False, read_only=True)
    class Meta:
        model = Horari
        fields = ['id', 'assignatura', 'professor', 'grup', 
        'dia_de_la_setmana', 'hora', 'nom_aula', 'aula','es_actiu','estat_sincronitzacio']

class ImpartirSerializer(serializers.ModelSerializer):
    horari = HorariSerializer(many=False, read_only=True)
    class Meta:
        model = Impartir
        fields = ['id', 'horari' ,'professor_guardia', 'professor_passa_llista', 'dia_impartir', 
        'dia_passa_llista', 'comentariImpartir', 'pot_no_tenir_alumnes', 'reserva']

class ControlAssistenciaIHoraAnteriorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlAssistenciaIHoraAnterior
        fields = ['id', 'alumne', 'estat', 'impartir', 'professor','estatHoraAnterior','nomAlumne','cognomsAlumne']

class ControlAssistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlAssistencia
        fields = ['id', 'alumne', 'estat', 'impartir', 'professor', 
            'swaped', 'estat_backup', 'professor_backup', 'relacio_familia_revisada', 'relacio_familia_notificada']
