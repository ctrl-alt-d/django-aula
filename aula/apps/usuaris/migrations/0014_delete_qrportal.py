from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("alumnes", "0024_remove_alumne_usuaris_app_associats"),
        ("usuaris", "0013_responsableuser_notifusuari"),
    ]

    operations = [
        migrations.DeleteModel(
            name="QRPortal",
        ),
    ]
