from django import template
from django.template import  NodeList, Variable
from django.contrib.auth.models import Group

register = template.Library()

#http://djangosnippets.org/snippets/390/

@register.tag()
def ifusergroup(parser, token):
    """ Check to see if the currently logged in user belongs to a specific
    group. Requires the Django authentication contrib app and middleware.

    Usage: {% ifusergroup Admins %} ... {% endifusergroup %}, or
           {% ifusergroup Admins %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        _, group = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifusergroup' requires 1 argument.")
    
    nodelist_true = parser.parse(('else', 'endifusergroup'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifusergroup',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return GroupCheckNode(group, nodelist_true, nodelist_false)


class GroupCheckNode(template.Node):
    def __init__(self, group, nodelist_true, nodelist_false):
        self.group = group
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = Variable('user').resolve(context)
        
        if not user.is_authenticated:
            return self.nodelist_false.render(context)

        #if user.is_staff:
        #    return self.nodelist_true.render(context)

        try:
            group = Group.objects.get(name=self.group)
        except Group.DoesNotExist:
            return self.nodelist_false.render(context)
            
        if group in user.groups.all():
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


#-------------------------------------------------------------------

@register.tag()
def ifusertutor(parser, token):

    nodelist_true = parser.parse(('else', 'endifusertutor'))
    token = parser.next_token()
    
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifusertutor',))
        parser.delete_first_token()
    else:
        nodelist_false = NodeList()
    
    return TutorCheckNode(nodelist_true, nodelist_false)


class TutorCheckNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
    def render(self, context):
        user = Variable('user').resolve(context)
        
        if not user.is_authenticated:
            return self.nodelist_false.render(context)

        if user.is_staff:
            return self.nodelist_true.render(context)

        try:
            from aula.apps.usuaris.models import User2Professor
            professor = User2Professor( user )
        except:
            return self.nodelist_false.render(context)
            
        if professor.tutor_set.count() > 0 or professor.tutorindividualitzat_set.count() > 0:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


@register.filter(name='valid_alert')
def valid_alert(value):
    valid = ( 'alert', 'warning', 'error', 'info', 'success')
    try:
        tag = next( x for x in  value.lower().split() if x in valid  )
    except StopIteration:
        tag = 'warning'
    return tag.replace( 'error', 'danger')


