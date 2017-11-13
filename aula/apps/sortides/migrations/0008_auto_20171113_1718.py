# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sortides', '0007_auto_20171113_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sortida',
            name='calendari_desde',
            field=models.DateTimeField(help_text="Horari real de l'activitat, hora de sortida, aquest horari, a m\xe9s, es publicar\xe0 al calendari del Centre", verbose_name='Horari real, des de:'),
        ),
    ]
