# Generated by Django 5.0.9 on 2025-02-18 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('presencia', '0012_rename_presencia_controlassiste_alumne_id_estat_id_relac_8957bdde_idx_presencia_c_alumne__6961f9_idx'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='controlassistencia',
            name='presencia_c_alumne__6961f9_idx',
        ),
    ]
