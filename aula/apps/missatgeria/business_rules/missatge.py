# This Python file uses the following encoding: utf-8

from datetime import datetime

def missatge_clean(instance):
    #
    #pre-save
    #
    instance.data = datetime.now()
    pass

def missatge_pre_save(sender, instance, **kwargs):
    missatge_clean( instance  )
    pass

def missatge_post_save(sender, instance, created, **kwargs):
    pass

def missatge_pre_delete( sender, instance, **kwargs):
    pass

