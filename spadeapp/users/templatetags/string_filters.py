from django import template

register = template.Library()


@register.filter
def replace(value, arg):
    old_string, new_string = arg.split("|")
    return value.replace(old_string, new_string)
