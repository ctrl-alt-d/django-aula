from aula.apps.alumnes.models import Alumne

#-------------------------------------------------------------------------------------

def alumne_post_save(sender, instance, created, **kwargs):
    if instance.user_associat is None:
        from aula.apps.usuaris.models import AlumneUser as AU
        user_associat, new = AU.objects.get_or_create( username='almn{0}'.format( instance.pk ) )
        if new:
            from django.contrib.auth.models import Group as G
            ga, _ = G.objects.get_or_create( name='alumne' )        
            user_associat.is_active = False
            user_associat.groups.add(ga)
            user_associat.save()
        instance.user_associat_id = user_associat.pk      
        instance.user_associat = user_associat
        Alumne.objects.filter( pk = instance.pk ).update( user_associat = user_associat )
        resp1, resp2 = instance.get_responsables()
        if instance.responsable_preferent and resp1!=instance.responsable_preferent and resp2!=instance.responsable_preferent: 
            instance.responsable_preferent=None
            Alumne.objects.filter( pk = instance.pk ).update( responsable_preferent = None )
        

