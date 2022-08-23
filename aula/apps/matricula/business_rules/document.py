# This Python file uses the following encoding: utf-8
import os
from django.conf import settings

def document_post_delete( sender, instance, **lwargs ):

    try:
        if instance.fitxer:
            os.remove(os.path.join(settings.PRIVATE_STORAGE_ROOT, instance.fitxer.name))
    except PermissionError as e:
        print("document_post_delete-Error accés",str(e))
