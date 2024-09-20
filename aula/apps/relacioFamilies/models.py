from django.db import models
from private_storage.fields import PrivateFileField
from django.conf import settings
from aula.apps.relacioFamilies.business_rules.docattach import docattach_post_delete


class EmailPendent(models.Model):
    subject = models.TextField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    fromemail = models.CharField(max_length=100, null=True, blank=True)
    toemail = models.TextField(null=True, blank=True)

    def __str__(self):
        pendents = list(eval(self.toemail)) if bool(self.toemail) else []
        pendents = (
            pendents
            if len(pendents) <= 2
            else (str(pendents[0]) + " i altres ... total:" + str(len(pendents)))
        )
        return str(self.subject) + ": " + str(self.fromemail) + "->" + str(pendents)


class DocAttach(models.Model):
    fitxer = PrivateFileField(
        "Fitxer adjunt",
        upload_to="email/",
        max_file_size=settings.FILE_UPLOAD_MAX_MEMORY_SIZE,
    )
    email = models.ForeignKey(EmailPendent, on_delete=models.CASCADE, blank=True)

    class Meta:
        verbose_name = "Attach File"
        verbose_name_plural = "Attach Files"

    def __str__(self):
        return str(self.fitxer.name) + ((" " + str(self.email)) if self.email else "")


from django.db.models.signals import post_delete

post_delete.connect(docattach_post_delete, sender=DocAttach)
