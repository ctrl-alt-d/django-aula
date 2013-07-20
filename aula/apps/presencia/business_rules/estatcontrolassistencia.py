# This Python file uses the following encoding: utf-8

#-------------EstatControlAssistencia-------------------------------------------------------------      

def estatControlAssistencia_clean( instance ):
    pass

def estatControlAssistencia_pre_delete( sender, instance, **kwargs):
    pass
    
def estatControlAssistencia_pre_save(sender, instance,  **kwargs):
    instance.clean()

def estatControlAssistencia_post_save(sender, instance, created, **kwargs):
    pass

