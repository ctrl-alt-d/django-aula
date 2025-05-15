from aula.apps.relacioFamilies.models import Responsable

def responsable_post_save(sender, instance, created, **kwargs):
    if instance.user_associat is None:
        from aula.apps.usuaris.models import ResponsableUser
        user_associat, new = ResponsableUser.objects.get_or_create( username='resp{0}'.format( instance.pk ) )
        if new:
            from django.contrib.auth.models import Group as G
            ga, _ = G.objects.get_or_create( name='alumne' )
            user_associat.is_active = False
            user_associat.groups.add(ga)
            user_associat.save()
        instance.user_associat_id = user_associat.pk      
        instance.user_associat = user_associat
        Responsable.objects.filter( pk = instance.pk ).update( user_associat = user_associat )
    