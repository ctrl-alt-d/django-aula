# Generated by Django 5.0.9 on 2025-02-20 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaluacioQualitativa', '0005_auto_20201021_1011'),
        ('usuaris', '0013_responsableuser_notifusuari'),
    ]

    operations = [
        migrations.AddField(
            model_name='respostaavaluacioqualitativa',
            name='notificacions_familia',
            field=models.ManyToManyField(db_index=True, to='usuaris.notifusuari'),
        ),
    ]
