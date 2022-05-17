from rest_framework import serializers


class DarreraSincronitzacioSerializer(serializers.Serializer):
    last_sync_date = serializers.DateTimeField()