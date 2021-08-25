from django.db import models

class EmailPendent(models.Model):
    subject=models.TextField(null=True, blank=True)
    message=models.TextField(null=True, blank=True)
    fromemail=models.CharField(max_length=100, null=True, blank=True)
    toemail=models.CharField( max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.subject) + ': ' + str(self.fromemail) + '->' + str(self.toemail)
