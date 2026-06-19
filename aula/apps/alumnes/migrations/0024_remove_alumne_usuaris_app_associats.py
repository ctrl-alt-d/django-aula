from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("alumnes", "0023_alter_alumne_aruco_marker"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="alumne",
            name="usuaris_app_associats",
        ),
    ]
