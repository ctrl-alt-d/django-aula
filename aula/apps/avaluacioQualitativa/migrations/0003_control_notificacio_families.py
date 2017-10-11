# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaluacioQualitativa', '0002_dates_obrir_tancar_portal'),
    ]

    operations = [
        migrations.AddField(
            model_name='respostaavaluacioqualitativa',
            name='relacio_familia_notificada',
            field=models.DateTimeField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='respostaavaluacioqualitativa',
            name='relacio_familia_revisada',
            field=models.DateTimeField(null=True, editable=False),
        ),
    ]
