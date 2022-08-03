from django import template

register = template.Library()

@register.simple_tag
def user_is_editor(object, user):
    if object:
        return object.user_is_editor(user)
    else:
        #if there is no object, then the user can create one
        return True
