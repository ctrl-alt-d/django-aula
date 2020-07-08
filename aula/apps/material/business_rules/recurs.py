
# This Python file uses the following encoding: utf-8

def recurs_clean(instance):
    pass


def recurs_pre_delete(sender, instance, **kwargs):
    pass


def recurs_pre_save(sender, instance, **kwargs):
    instance.clean()


def recurs_post_save(sender, instance, created, **kwargs):
    pass