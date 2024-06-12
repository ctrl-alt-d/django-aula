# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
from rest_framework import serializers

class QRTokenSerializer(serializers.Serializer):
    key = serializers.CharField(max_length=40)
    born_date = serializers.DateField()

    def validate_clau(self, value):
        """
        Validacions del token.
        """
        if len(value)<5:
            raise serializers.ValidationError("Aquest token és raro")

        return value

class DarreraSincronitzacioSerializer(serializers.Serializer):
    last_sync_date = serializers.DateTimeField()

class PagamentRealitzatSerializer(serializers.Serializer):
    codi_pagament = serializers.CharField()
    data_hora_pagament = serializers.DateTimeField()
    ordre_pagament = serializers.CharField(max_length=12)

