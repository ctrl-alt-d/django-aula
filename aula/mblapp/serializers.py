# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
from rest_framework import serializers

class QRTokenSerializer(serializers.Serializer):
    clau = serializers.CharField(max_length=40)

    def validate_clau(self, value):
        """
        Validacions del token.
        """
        if len(value)<5:
            raise serializers.ValidationError("Aquest token és raro")

        return value

class DarreraSincronitzacioSerializer(serializers.Serializer):
    darrera_sincronitzacio = serializers.DateTimeField()



