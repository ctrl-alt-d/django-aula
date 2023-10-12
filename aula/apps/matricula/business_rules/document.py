# This Python file uses the following encoding: utf-8
import os
from django.conf import settings

def document_post_delete( sender, instance, **lwargs ):

    try:
        if instance.fitxer:
            doc=os.path.join(settings.PRIVATE_STORAGE_ROOT, instance.fitxer.name)
            if os.path.exists(doc):
                os.remove(doc)
    except Exception as e:
        print("document_post_delete-Error",str(e))
