from django import template

register = template.Library()

#http://djangosnippets.org/snippets/390/

# tag to get the value of a field by name in template
@register.simple_tag
def get_value_from_key(object, key):
    # is it necessary to check isinstance(object, dict) here?
    return object[key-1]