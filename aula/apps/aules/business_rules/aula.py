
# This Python file uses the following encoding: utf-8

def aula_clean(instance):
    pass


def aula_pre_delete(sender, instance, **kwargs):
    pass


def aula_pre_save(sender, instance, **kwargs):
    instance.clean()


def aula_post_save(sender, instance, created, **kwargs):
    pass