from django import template

register = template.Library()

@register.simple_tag
def user_is_editor(object, user):
    return object.user_is_editor(user)
