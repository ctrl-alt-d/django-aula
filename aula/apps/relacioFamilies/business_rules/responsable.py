from aula.apps.relacioFamilies.models import Responsable

def responsable_post_save(sender, instance, created, **kwargs):
    if instance.user_associat is None:
        from aula.apps.usuaris.models import ResponsableUser
        user_associat, new = ResponsableUser.objects.get_or_create( username='resp{0}'.format( instance.pk ) )
        if new:
            from django.contrib.auth.models import Group as G
            ga, _ = G.objects.get_or_create( name='alumne' )
            # De manera provisional activa l'usuari i assigna contrasenya igual a l'username
            # Així no fa falta fer la benvinguda i simplifica fer proves
            user_associat.is_active = True # TODO usuariResponsable False
            user_associat.set_password(user_associat.username) # TODO usuariResponsable no s'ha de fer
            user_associat.groups.add(ga)
            user_associat.save()
            user_associat.responsable.motiu_bloqueig='' # TODO usuariResponsable no s'ha de fer
            user_associat.responsable.save() # TODO usuariResponsable no s'ha de fer
        instance.user_associat_id = user_associat.pk      
        instance.user_associat = user_associat
        Responsable.objects.filter( pk = instance.pk ).update( user_associat = user_associat )
    